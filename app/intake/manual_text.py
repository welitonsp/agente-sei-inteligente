"""Entrada manual de texto para o MVP externo/local.

Este modulo implementa o fluxo seguro de `IMPORT_TEXT` descrito em docs/14 e
docs/27. Ele nao acessa o SEI, nao pesquisa processo por numero e nao salva o
texto integral: persiste apenas metadados, hash e resumo estrutural.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from app.core import audit
from app.sei.sei_action_guard import GuardRequest, GuardResult, evaluate
from app.storage.db import session_scope
from app.storage.models import Document, Process


_DATE_ISO = re.compile(r"\b(20\d{2})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\b")
_DATE_BR = re.compile(r"\b([0-2]?\d|3[01])/(0?[1-9]|1[0-2])/(20\d{2})\b")
_TIME = re.compile(r"\b([01]?\d|2[0-3])[:h]([0-5]\d)\b", re.IGNORECASE)
_LOCAL = re.compile(r"\blocal\s*:\s*([^\n\r.;]+)", re.IGNORECASE)

_EVENT_KEYWORDS = (
    "reuniao",
    "reunião",
    "convocacao",
    "convocação",
    "curso",
    "solenidade",
    "evento",
    "audiencia",
    "audiência",
)

_DEADLINE_KEYWORDS = (
    "prazo",
    "ate",
    "até",
    "data limite",
    "encaminhar ate",
    "encaminhar até",
    "responder ate",
    "responder até",
)


@dataclass(frozen=True)
class ManualTextRequest:
    titulo: str
    texto: str
    processo_sei: str = ""
    origem: str = "web"
    usuario_local: str = ""
    estacao: str = ""
    source_reference: str = "texto_colado"


@dataclass(frozen=True)
class ExtractedEvent:
    ha_evento: bool = False
    titulo: str = ""
    data: str | None = None
    horario_inicio: str | None = None
    horario_fim: str | None = None
    local: str = ""
    publico_alvo: str = ""
    agenda_sugerida: bool = False
    campos_pendentes: list[str] = field(default_factory=list)
    confianca: float = 0.0

    def to_contract(self) -> dict[str, Any]:
        return {
            "ha_evento": self.ha_evento,
            "titulo": self.titulo,
            "data": self.data,
            "horario_inicio": self.horario_inicio,
            "horario_fim": self.horario_fim,
            "local": self.local,
            "publico_alvo": self.publico_alvo,
            "agenda_sugerida": self.agenda_sugerida,
            "campos_pendentes": self.campos_pendentes,
            "confianca": self.confianca,
        }


@dataclass(frozen=True)
class ExtractedDeadline:
    ha_prazo: bool = False
    data_limite: str | None = None
    hora_limite: str | None = None
    tipo_prazo: str = ""
    risco: str = "baixo"
    texto_fonte: str = ""
    lembretes_sugeridos: list[int] = field(default_factory=list)
    confianca: float = 0.0

    def to_contract(self) -> dict[str, Any]:
        return {
            "ha_prazo": self.ha_prazo,
            "data_limite": self.data_limite,
            "hora_limite": self.hora_limite,
            "tipo_prazo": self.tipo_prazo,
            "risco": self.risco,
            "texto_fonte": self.texto_fonte,
            "lembretes_sugeridos": self.lembretes_sugeridos,
            "confianca": self.confianca,
        }


@dataclass(frozen=True)
class ManualTextResult:
    status: str
    processo_id: int | None
    documento_id: int | None
    text_hash: str
    resumo_executivo: str
    evento: ExtractedEvent
    prazo: ExtractedDeadline
    campos_pendentes: list[str]
    revisao_humana_obrigatoria: bool
    confianca: float
    audit_log_ids: list[int] = field(default_factory=list)
    motivo: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resultado": {
                "processo_id": self.processo_id,
                "documento_id": self.documento_id,
                "text_hash": self.text_hash,
                "resumo_executivo": self.resumo_executivo,
                "evento": self.evento.to_contract(),
                "prazo": self.prazo.to_contract(),
            },
            "confianca": self.confianca,
            "fontes": ["texto_colado"] if self.text_hash else [],
            "campos_pendentes": self.campos_pendentes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_sugeridas": _suggested_actions(self.evento, self.prazo),
            "acoes_bloqueadas": [],
            "logs": self.audit_log_ids,
            "motivo": self.motivo,
        }


def analyze_text(request: ManualTextRequest) -> ManualTextResult:
    """Importa e analisa texto manual sem acessar SEI real.

    A resposta e propositalmente conservadora: a analise local usa heuristicas
    simples e sempre exige revisao humana antes de qualquer agenda/minuta.
    """
    texto = request.texto.strip()
    campos_pendentes = _missing_fields(request)
    if not texto:
        audit_id = audit.record(
            action="LER_DOCUMENTO",
            result="precisa_revisao",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Texto manual ausente.",
            metadata={"origem": request.origem, "modo_leitura": "texto_colado"},
        )
        return ManualTextResult(
            status="precisa_revisao",
            processo_id=None,
            documento_id=None,
            text_hash="",
            resumo_executivo="Texto manual ausente. Informe o conteudo para analise.",
            evento=ExtractedEvent(campos_pendentes=["texto"]),
            prazo=ExtractedDeadline(),
            campos_pendentes=campos_pendentes,
            revisao_humana_obrigatoria=True,
            confianca=0.0,
            audit_log_ids=[audit_id],
            motivo="Texto obrigatorio ausente.",
        )

    read_guard = _guard("LER_DOCUMENTO", request)
    summarize_guard = _guard("RESUMIR", request)
    audit_ids = [
        audit.record_guard_decision(_guard_request("LER_DOCUMENTO", request), read_guard),
        audit.record_guard_decision(_guard_request("RESUMIR", request), summarize_guard),
    ]

    if not (read_guard.permitido and summarize_guard.permitido):
        return ManualTextResult(
            status="bloqueado",
            processo_id=None,
            documento_id=None,
            text_hash="",
            resumo_executivo="Analise bloqueada pelo guardiao de seguranca.",
            evento=ExtractedEvent(),
            prazo=ExtractedDeadline(),
            campos_pendentes=campos_pendentes,
            revisao_humana_obrigatoria=True,
            confianca=0.0,
            audit_log_ids=audit_ids,
            motivo="Guardiao bloqueou a leitura/resumo.",
        )

    text_hash = _hash_text(texto)
    evento = extract_event(texto, request.titulo)
    prazo = extract_deadline(texto)
    resumo = _structural_summary(
        title=request.titulo,
        text=texto,
        event=evento,
        deadline=prazo,
    )

    processo_id, documento_id = _persist_metadata(
        request=request,
        text_hash=text_hash,
        summary=resumo,
        confidence=_confidence(evento, prazo),
    )

    audit_ids.append(
        audit.record(
            action="REGISTRAR_LOG",
            result="permitido",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Texto manual importado para analise local.",
            metadata={
                "origem": request.origem,
                "modo_leitura": "texto_colado",
                "documento_id": documento_id,
                "text_hash": text_hash,
                "texto_caracteres": len(texto),
                "evento_detectado": evento.ha_evento,
                "prazo_detectado": prazo.ha_prazo,
            },
        )
    )

    return ManualTextResult(
        status="precisa_revisao",
        processo_id=processo_id,
        documento_id=documento_id,
        text_hash=text_hash,
        resumo_executivo=resumo,
        evento=evento,
        prazo=prazo,
        campos_pendentes=campos_pendentes,
        revisao_humana_obrigatoria=True,
        confianca=_confidence(evento, prazo),
        audit_log_ids=audit_ids,
        motivo="Analise local preliminar; revisao humana obrigatoria.",
    )


def extract_event(text: str, title: str = "") -> ExtractedEvent:
    normalized = _normalize(text)
    has_event = any(keyword in normalized for keyword in _EVENT_KEYWORDS)
    date = _first_date(text)
    time = _first_time(text)
    local = _first_local(text)

    if not (has_event or date):
        return ExtractedEvent(campos_pendentes=["data", "horario_inicio", "local"])

    pending = []
    if not date:
        pending.append("data")
    if not time:
        pending.append("horario_inicio")
    if not local:
        pending.append("local")

    return ExtractedEvent(
        ha_evento=has_event and bool(date),
        titulo=(title.strip() or "Evento identificado em texto manual"),
        data=date,
        horario_inicio=time,
        local=local,
        agenda_sugerida=has_event and bool(date) and not pending,
        campos_pendentes=pending,
        confianca=0.65 if has_event and date and time else 0.4 if has_event else 0.2,
    )


def extract_deadline(text: str) -> ExtractedDeadline:
    normalized = _normalize(text)
    has_keyword = any(keyword in normalized for keyword in _DEADLINE_KEYWORDS)
    date = _first_date(text)
    time = _first_time(text)
    if not (has_keyword and date):
        return ExtractedDeadline()

    risco = "urgente" if any(w in normalized for w in ("urgente", "imediato")) else "medio"
    return ExtractedDeadline(
        ha_prazo=True,
        data_limite=date,
        hora_limite=time,
        tipo_prazo="administrativo",
        risco=risco,
        texto_fonte="texto_colado",
        lembretes_sugeridos=[1440, 0] if risco == "urgente" else [4320, 1440],
        confianca=0.6 if time else 0.45,
    )


def _guard(action: str, request: ManualTextRequest) -> GuardResult:
    return evaluate(_guard_request(action, request))


def _guard_request(action: str, request: ManualTextRequest) -> GuardRequest:
    return GuardRequest(
        acao_solicitada=action,
        origem="manual_text_intake",
        usuario_local=request.usuario_local,
        estacao=request.estacao,
        processo_sei=request.processo_sei,
        justificativa="Importacao manual de texto no MVP externo/local.",
        aprovado_por_humano=True,
    )


def _persist_metadata(
    *,
    request: ManualTextRequest,
    text_hash: str,
    summary: str,
    confidence: float,
) -> tuple[int, int]:
    with session_scope() as session:
        process = Process(
            sei_number=request.processo_sei.strip() or None,
            subject=request.titulo.strip() or None,
            origin=request.origem,
            status="recebida",
        )
        session.add(process)
        session.flush()

        document = Document(
            process_id=process.id,
            source_type="texto",
            source_reference=request.source_reference,
            title=request.titulo.strip() or None,
            text_hash=text_hash,
            extracted_text_path=None,
            summary=summary,
            classification="texto_manual",
            confidence=confidence,
        )
        session.add(document)
        session.flush()
        return process.id, document.id


def _missing_fields(request: ManualTextRequest) -> list[str]:
    missing = []
    if not request.texto.strip():
        missing.append("texto")
    if not request.titulo.strip():
        missing.append("titulo")
    if not request.processo_sei.strip():
        missing.append("processo_sei")
    return missing


def _suggested_actions(event: ExtractedEvent, deadline: ExtractedDeadline) -> list[str]:
    actions = []
    if event.ha_evento:
        actions.append("REVISAR_EVENTO")
    if deadline.ha_prazo:
        actions.append("REVISAR_PRAZO")
    return actions


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _first_date(text: str) -> str | None:
    iso = _DATE_ISO.search(text)
    if iso:
        return iso.group(0)
    br = _DATE_BR.search(text)
    if br:
        day, month, year = br.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return None


def _first_time(text: str) -> str | None:
    match = _TIME.search(text)
    if not match:
        return None
    hour, minute = match.groups()
    return f"{int(hour):02d}:{minute}"


def _first_local(text: str) -> str:
    match = _LOCAL.search(text)
    if not match:
        return ""
    return " ".join(match.group(1).strip().split())


def _structural_summary(
    *,
    title: str,
    text: str,
    event: ExtractedEvent,
    deadline: ExtractedDeadline,
) -> str:
    title_part = title.strip() or "sem titulo informado"
    parts = [
        f"Texto manual recebido para analise local: {title_part}.",
        f"Foram recebidos {len(text)} caracteres; o texto integral nao foi persistido.",
    ]
    if event.ha_evento:
        parts.append(
            f"Possivel evento em {event.data or 'data indefinida'}"
            f"{f' as {event.horario_inicio}' if event.horario_inicio else ''}."
        )
    if deadline.ha_prazo:
        parts.append(f"Possivel prazo administrativo em {deadline.data_limite}.")
    parts.append("Revisao humana obrigatoria antes de qualquer providencia.")
    return " ".join(parts)


def _confidence(event: ExtractedEvent, deadline: ExtractedDeadline) -> float:
    return max(0.25, event.confianca, deadline.confianca)
