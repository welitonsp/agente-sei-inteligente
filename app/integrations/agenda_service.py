"""Skill `agenda-oficiais`: prepara e cria eventos no Google Agenda.

Regras (docs/04 e docs/24):
- Titulo padrao: [Tipo] Nome do evento - Unidade/Origem
- Observacao padronizada com processo, origem, assunto, prazo etc.
- Lembretes por tipo de evento.
- Deduplicacao por: processo + titulo + data + horario + local.
- CRIAR_EVENTO_AGENDA e acao SENSIVEL: exige aprovacao humana explicita.
- Toda decisao e auditada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

from app.core import audit
from app.core.config import get_settings
from app.integrations.calendar_backend import CalendarBackend, CalendarEvent
from app.integrations.contacts_resolver import _clean_emails as _normalize_emails
from app.integrations.ics_reader import IcsEvent, find_equivalent, read_calendar
from app.sei.sei_action_guard import GuardRequest, evaluate
from app.storage.db import session_scope
from app.storage.models import Event

# Provedor de eventos do calendario real (feed ICS). Devolve a lista de eventos
# ja existentes para a checagem de duplicidade.
IcsEventsProvider = Callable[[], list[IcsEvent]]


def settings_ics_provider() -> list[IcsEvent]:
    """Provider padrao: le o feed ICS a partir da URL secreta no ambiente.

    Fallback seguro (regra 10): se a URL nao estiver configurada, devolve lista
    vazia (sem duplicatas conhecidas), permitindo o fluxo seguir. A URL NUNCA e
    logada nem retornada (regra 9).
    """
    url = get_settings().google_calendar_ics_url
    if not url:
        return []
    return read_calendar(url)

# Offset fixo de America/Sao_Paulo (sem horario de verao no Brasil atual).
_TZ_OFFSET = "-03:00"

# Lembretes em minutos antes do evento, por tipo (docs/04).
REMINDERS_BY_TYPE: dict[str, list[int]] = {
    "comum": [1440, 60],  # 1 dia, 1 hora
    "curso": [4320, 1440, 60],  # 3 dias, 1 dia, 1 hora
    "solenidade": [4320, 1440, 60],
    "prazo": [10080, 4320, 1440, 0],  # 7 dias, 3 dias, 1 dia, no dia
    "prazo_urgente": [1440, 0],  # 1 dia, no dia (imediato tratado a parte)
}


def reminders_for(event_type: str | None) -> list[int]:
    key = (event_type or "comum").strip().lower()
    return REMINDERS_BY_TYPE.get(key, REMINDERS_BY_TYPE["comum"])


def build_title(event_type: str | None, nome: str, origem: str) -> str:
    tipo = (event_type or "Evento").strip().capitalize()
    base = f"[{tipo}] {nome.strip()}"
    if origem.strip():
        base += f" - {origem.strip()}"
    return base


def build_observation(ctx: dict[str, Any]) -> str:
    """Monta o campo observacao no formato padrao (docs/04)."""
    campos = [
        ("Processo SEI", ctx.get("processo_sei", "")),
        ("Origem", ctx.get("origem", "")),
        ("Assunto", ctx.get("assunto", "")),
        ("Resumo", ctx.get("resumo", "")),
        ("Providencia", ctx.get("providencia", "")),
        ("Data", ctx.get("data", "")),
        ("Horario", ctx.get("horario", "")),
        ("Local", ctx.get("local", "")),
        ("Responsavel", ctx.get("responsavel", "")),
        ("Observacao", ctx.get("observacao", "")),
    ]
    return "\n".join(f"{rotulo}: {valor}" for rotulo, valor in campos)


def deduplication_key(
    processo: str, titulo: str, data: str, horario: str, local: str
) -> str:
    partes = [processo, titulo, data, horario, local]
    norm = "|".join(p.strip().lower() for p in partes)
    return norm


@dataclass
class EventInput:
    titulo: str
    data: str  # YYYY-MM-DD
    horario_inicio: str  # HH:MM
    horario_fim: str = ""  # HH:MM (opcional; default +1h)
    local: str = ""
    descricao: str = ""
    tipo: str = "comum"
    origem: str = ""


@dataclass
class AgendaRequest:
    evento: EventInput
    processo_sei: str = ""
    # E-mails ja resolvidos dos Oficiais (ver contacts_resolver). No modo
    # google_contacts, vem do marcador "OFICIAIS" do Google Contatos.
    convidados: list[str] = field(default_factory=list)
    # Quando True (padrao), nao cria evento de convocacao sem nenhum convidado.
    exigir_convidados: bool = True
    # Dispara convite real (sendUpdates=all). So tem efeito em backend real.
    enviar_convites: bool = False
    contexto_observacao: dict[str, Any] = field(default_factory=dict)
    usuario_local: str = ""
    aprovado_por_humano: bool = False


@dataclass
class AgendaResult:
    pode_criar: bool
    precisa_revisao: bool
    motivo: str
    google_event_id: str = ""
    deduplication_key: str = ""
    campos_pendentes: list[str] = field(default_factory=list)
    convidados_count: int = 0
    # Estado claro do resultado (regra 8): simulated | created | duplicate |
    # incompleto | sem_convidados | bloqueado | precisa_revisao.
    status: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "pode_criar": self.pode_criar,
            "precisa_revisao": self.precisa_revisao,
            "motivo": self.motivo,
            "google_event_id": self.google_event_id,
            "deduplication_key": self.deduplication_key,
            "campos_pendentes": self.campos_pendentes,
            "status": self.status,
        }


def _missing_fields(ev: EventInput) -> list[str]:
    pend = []
    if not ev.titulo.strip():
        pend.append("titulo")
    if not ev.data.strip():
        pend.append("data")
    if not ev.horario_inicio.strip():
        pend.append("horario_inicio")
    return pend


def _to_iso(data: str, horario: str) -> str:
    return f"{data}T{horario}:00{_TZ_OFFSET}"


def _end_iso(ev: EventInput) -> str:
    if ev.horario_fim.strip():
        return _to_iso(ev.data, ev.horario_fim)
    inicio = datetime.strptime(f"{ev.data} {ev.horario_inicio}", "%Y-%m-%d %H:%M")
    fim = inicio + timedelta(hours=1)
    return f"{fim.strftime('%Y-%m-%dT%H:%M:%S')}{_TZ_OFFSET}"


def create_calendar_event(
    request: AgendaRequest,
    backend: CalendarBackend,
    calendar_id: str,
    ics_provider: IcsEventsProvider | None = None,
) -> AgendaResult:
    """Avalia e (se permitido) cria/simula o evento. Sempre audita a decisao.

    ics_provider: fonte dos eventos do calendario real para checagem de
    duplicidade. Em producao, o orquestrador injeta `settings_ics_provider`.
    Se None, a checagem ICS e pulada (fallback seguro: nao bloqueia).
    """
    ev = request.evento

    # 1) Campos obrigatorios.
    pendentes = _missing_fields(ev)
    if pendentes:
        return AgendaResult(
            pode_criar=False,
            precisa_revisao=True,
            motivo="Campos obrigatorios ausentes para criar evento.",
            campos_pendentes=pendentes,
            status="incompleto",
        )

    # 2) Convidados (Oficiais). Regra 6: sem nenhum e-mail, nao cria evento de
    #    convocacao com convidados; registra erro claro (apenas a contagem).
    convidados = _normalize_emails(request.convidados)
    if request.exigir_convidados and not convidados:
        audit.record(
            action="CRIAR_EVENTO_AGENDA",
            result="erro",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Nenhum e-mail de convidado encontrado no marcador de Oficiais.",
            metadata={"convidados_count": 0},
        )
        return AgendaResult(
            pode_criar=False,
            precisa_revisao=True,
            motivo=(
                "Nenhum convidado (Oficiais) encontrado. Verifique o marcador "
                "'OFICIAIS' no Google Contatos e as credenciais da People API."
            ),
            campos_pendentes=["convidados"],
            convidados_count=0,
            status="sem_convidados",
        )

    titulo = build_title(ev.tipo, ev.titulo, ev.origem)
    dedup = deduplication_key(
        request.processo_sei, titulo, ev.data, ev.horario_inicio, ev.local
    )

    # 2) Deduplicacao contra o banco local.
    with session_scope() as session:
        existente = (
            session.query(Event)
            .filter(Event.deduplication_key == dedup)
            .one_or_none()
        )
        if existente is not None:
            audit.record(
                action="CRIAR_EVENTO_AGENDA",
                result="duplicate",
                actor_id=request.usuario_local or None,
                target_type="processo_sei",
                target_id=request.processo_sei or None,
                reason="Evento ja existente para a mesma chave de duplicidade.",
                metadata={"deduplication_key": dedup, "event_id": existente.id},
            )
            return AgendaResult(
                pode_criar=False,
                precisa_revisao=False,
                motivo="Evento ja existe (duplicidade); vinculado ao registro existente.",
                google_event_id=existente.google_event_id or "",
                deduplication_key=dedup,
                status="duplicate",
            )

    # 2b) Deduplicacao contra o CALENDARIO REAL (feed ICS, somente leitura).
    #     Fallback seguro (regra 10): falha de acesso ou ICS ausente nao bloqueia.
    if ics_provider is not None:
        try:
            eventos_reais = ics_provider()
        except Exception:
            eventos_reais = None  # falha de acesso ao ICS -> nao bloqueia
            audit.record(
                action="CRIAR_EVENTO_AGENDA",
                result="ics_indisponivel",
                actor_id=request.usuario_local or None,
                target_type="processo_sei",
                target_id=request.processo_sei or None,
                reason="Feed ICS indisponivel; checagem de duplicidade no calendario real pulada.",
                metadata={"deduplication_key": dedup},
            )
        if eventos_reais:
            equivalente = find_equivalent(
                eventos_reais,
                title=titulo,
                date=ev.data,
                time=ev.horario_inicio,
                location=ev.local,
                processo_sei=request.processo_sei,
            )
            if equivalente is not None:
                audit.record(
                    action="CRIAR_EVENTO_AGENDA",
                    result="duplicate",
                    actor_id=request.usuario_local or None,
                    target_type="processo_sei",
                    target_id=request.processo_sei or None,
                    reason="Evento equivalente ja existe no calendario real (ICS).",
                    metadata={
                        "deduplication_key": dedup,
                        "match_uid": equivalente.uid,
                        "data": ev.data,
                    },
                )
                return AgendaResult(
                    pode_criar=False,
                    precisa_revisao=False,
                    motivo="Evento bloqueado por duplicidade no calendario real.",
                    deduplication_key=dedup,
                    status="duplicate",
                )

    # 3) Guard: CRIAR_EVENTO_AGENDA e sensivel -> exige aprovacao humana.
    guard_req = GuardRequest(
        acao_solicitada="CRIAR_EVENTO_AGENDA",
        origem="agenda_service",
        usuario_local=request.usuario_local,
        processo_sei=request.processo_sei,
        aprovado_por_humano=request.aprovado_por_humano,
    )
    guard_res = evaluate(guard_req)
    audit.record_guard_decision(guard_req, guard_res)
    if not guard_res.permitido:
        return AgendaResult(
            pode_criar=False,
            precisa_revisao=guard_res.revisao_humana_obrigatoria,
            motivo=guard_res.motivo,
            deduplication_key=dedup,
            status="precisa_revisao"
            if guard_res.revisao_humana_obrigatoria
            else "bloqueado",
        )

    # 4) Cria o evento no backend e persiste o registro local.
    observ = build_observation(
        {
            "processo_sei": request.processo_sei,
            "origem": ev.origem,
            "local": ev.local,
            "data": ev.data,
            "horario": ev.horario_inicio,
            **request.contexto_observacao,
        }
    )
    cal_event = CalendarEvent(
        summary=titulo,
        start=_to_iso(ev.data, ev.horario_inicio),
        end=_end_iso(ev),
        location=ev.local,
        description=f"{ev.descricao}\n\n{observ}".strip(),
        attendees=convidados,
        reminders_minutes=reminders_for(ev.tipo),
    )
    # Regra 5/8: convite real (sendUpdates=all) apenas em backend real.
    send_invitations = bool(request.enviar_convites and getattr(backend, "is_real", False))
    external_id = backend.create_event(
        calendar_id, cal_event, send_invitations=send_invitations
    )

    is_real = bool(getattr(backend, "is_real", False))
    status = "created" if is_real else "simulated"

    with session_scope() as session:
        registro = Event(
            title=titulo,
            event_type=ev.tipo,
            location=ev.local,
            description=cal_event.description,
            deduplication_key=dedup,
            google_event_id=external_id,
            status=status,
        )
        session.add(registro)

    # Regra 7: auditar apenas a QUANTIDADE de convidados, nunca os e-mails.
    audit.record(
        action="CRIAR_EVENTO_AGENDA",
        result=status,
        actor_id=request.usuario_local or None,
        target_type="processo_sei",
        target_id=request.processo_sei or None,
        reason="Evento criado no calendario real."
        if is_real
        else "Evento novo simulado (dry-run).",
        metadata={
            "deduplication_key": dedup,
            "google_event_id": external_id,
            "convidados_count": len(convidados),
            "convites_enviados": send_invitations,
        },
    )
    return AgendaResult(
        pode_criar=True,
        precisa_revisao=False,
        motivo="Evento criado no calendario real."
        if is_real
        else "Evento novo simulado (dry-run).",
        google_event_id=external_id,
        deduplication_key=dedup,
        convidados_count=len(convidados),
        status=status,
    )
