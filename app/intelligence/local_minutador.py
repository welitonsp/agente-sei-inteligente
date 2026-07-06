"""Minutador administrativo local, zero custo e baseado em templates.

Nao usa IA paga, nao acessa o SEI e nao cria documento oficial. O resultado e
um rascunho copiavel para revisao humana.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.core import audit
from app.sei.sei_action_guard import GuardRequest, evaluate


VALID_DRAFT_TYPES = frozenset(
    {"despacho", "oficio", "informacao", "encaminhamento", "parte", "portaria", "memorando"}
)

OFFICIAL_ACTIONS_BLOCKED = [
    "ASSINAR_DOCUMENTO",
    "ENVIAR_PROCESSO",
    "TRAMITAR_PROCESSO",
    "CONCLUIR_PROCESSO",
    "CRIAR_DOCUMENTO_OFICIAL_NO_SEI",
]

_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class DraftRequest:
    assunto: str
    resumo: str = ""
    texto_base: str = ""
    processo_sei: str = ""
    tipo_minuta: str = ""
    unidade_destino: str = ""
    destinatario: str = ""
    providencia: str = ""
    prazo: str = ""
    evento: str = ""
    usuario_local: str = ""
    estacao: str = ""
    origem: str = "minutador_local"


@dataclass(frozen=True)
class DraftResult:
    status: str
    tipo_minuta: str
    texto: str
    providencia_sugerida: str
    campos_usados: list[str]
    alertas: list[str]
    campos_pendentes: list[str]
    revisao_humana_obrigatoria: bool
    confianca: float
    audit_log_ids: list[int] = field(default_factory=list)
    motivo: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resultado": {
                "tipo_minuta": self.tipo_minuta,
                "texto": self.texto,
                "providencia_sugerida": self.providencia_sugerida,
                "campos_usados": self.campos_usados,
                "alertas": self.alertas,
            },
            "confianca": self.confianca,
            "fontes": ["template_local", "regras_locais"],
            "campos_pendentes": self.campos_pendentes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_sugeridas": ["REVISAR_MINUTA", "COPIAR_MINUTA"],
            "acoes_bloqueadas": OFFICIAL_ACTIONS_BLOCKED,
            "logs": self.audit_log_ids,
            "motivo": self.motivo,
        }


def generate_draft(request: DraftRequest) -> DraftResult:
    """Gera rascunho administrativo local sem salvar ou escrever no SEI."""
    guard_request = GuardRequest(
        acao_solicitada="GERAR_MINUTA",
        origem=request.origem,
        usuario_local=request.usuario_local,
        estacao=request.estacao,
        processo_sei=request.processo_sei,
        justificativa="Geracao local de rascunho por template, sem escrita no SEI.",
        aprovado_por_humano=False,
    )
    guard_result = evaluate(guard_request)
    audit_ids = [audit.record_guard_decision(guard_request, guard_result)]
    if not guard_result.permitido:
        return DraftResult(
            status="bloqueado",
            tipo_minuta="",
            texto="Minuta bloqueada pelo guardiao de seguranca.",
            providencia_sugerida="Revisar solicitacao antes de prosseguir.",
            campos_usados=[],
            alertas=["Guardiao bloqueou a acao GERAR_MINUTA."],
            campos_pendentes=["tipo_minuta"],
            revisao_humana_obrigatoria=True,
            confianca=0.0,
            audit_log_ids=audit_ids,
            motivo=guard_result.motivo,
        )

    tipo = _normalize_type(request.tipo_minuta) or infer_draft_type(
        " ".join([request.assunto, request.resumo, request.texto_base])
    )
    campos_pendentes = _missing_fields(request, tipo)
    values = _template_values(request, tipo)
    texto = _render_template(tipo, values)
    providencia = request.providencia.strip() or _suggest_providence(tipo, request)
    campos_usados = _used_fields(request)
    confidence = _confidence(request, tipo, campos_pendentes)
    alertas = [
        "Rascunho local para revisao humana obrigatoria.",
        "Nao assinar, tramitar, enviar ou concluir automaticamente no SEI.",
        "Conferir nomes, datas, unidade destinataria, fundamento e prazo antes de usar.",
    ]
    if campos_pendentes:
        alertas.append("Ha campos pendentes; marcadores [PREENCHER] foram mantidos.")

    audit_ids.append(
        audit.record(
            action="GERAR_MINUTA",
            result="precisa_revisao",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Minuta local gerada por template; revisao humana obrigatoria.",
            metadata={
                "origem": request.origem,
                "tipo_minuta": tipo,
                "campos_pendentes": campos_pendentes,
                "confianca": confidence,
                "texto_integral_persistido": False,
            },
        )
    )

    return DraftResult(
        status="precisa_revisao",
        tipo_minuta=tipo,
        texto=texto,
        providencia_sugerida=providencia,
        campos_usados=campos_usados,
        alertas=alertas,
        campos_pendentes=campos_pendentes,
        revisao_humana_obrigatoria=True,
        confianca=confidence,
        audit_log_ids=audit_ids,
        motivo="Minuta local preliminar; revise antes de usar.",
    )


def infer_draft_type(text: str) -> str:
    """Classifica o tipo provavel de minuta por regras simples."""
    normalized = _normalize(text)
    if any(term in normalized for term in ("oficio", "resposta externa", "externo")):
        return "oficio"
    if any(term in normalized for term in ("informacao", "informar", "relato")):
        return "informacao"
    if any(term in normalized for term in ("encaminhamento", "encaminhar", "remeter")):
        return "encaminhamento"
    if any(term in normalized for term in ("parte", "relato de servico", "boletim")):
        return "parte"
    if any(term in normalized for term in ("portaria", "instauracao", "sindicancia", "ipm")):
        return "portaria"
    if any(term in normalized for term in ("memorando", "interno")):
        return "memorando"
    if any(term in normalized for term in ("providencia", "despacho", "prazo", "autos")):
        return "despacho"
    return "despacho"


def _render_template(tipo: str, values: dict[str, str]) -> str:
    if tipo == "oficio":
        return (
            "OFICIO\n\n"
            f"Processo SEI: {values['processo_sei']}\n"
            f"Assunto: {values['assunto']}\n\n"
            f"Senhor(a) {values['destinatario']},\n\n"
            "Em atencao ao expediente em referencia, informo que "
            f"{values['resumo']}.\n\n"
            f"Providencia sugerida: {values['providencia']}.\n"
            f"Prazo/evento: {values['prazo_evento']}.\n\n"
            "O presente texto e rascunho e deve ser revisado pela autoridade "
            "competente antes de qualquer uso oficial.\n\n"
            "Respeitosamente,"
        )
    if tipo == "informacao":
        return (
            "INFORMACAO\n\n"
            f"Processo SEI: {values['processo_sei']}\n"
            f"Assunto: {values['assunto']}\n\n"
            f"Trata-se de demanda relacionada a {values['resumo']}.\n\n"
            f"Providencia sugerida: {values['providencia']}.\n"
            f"Unidade/Responsavel: {values['unidade_destino']}.\n"
            f"Prazo/evento: {values['prazo_evento']}.\n\n"
            "Submete-se a presente informacao para analise e deliberacao da "
            "autoridade competente."
        )
    if tipo == "encaminhamento":
        return (
            "ENCAMINHAMENTO\n\n"
            f"Processo SEI: {values['processo_sei']}\n"
            f"Assunto: {values['assunto']}\n\n"
            f"Encaminha-se a demanda a {values['unidade_destino']} para "
            "conhecimento, analise e adocao das providencias cabiveis.\n\n"
            f"Resumo: {values['resumo']}.\n"
            f"Providencia sugerida: {values['providencia']}.\n"
            f"Prazo/evento: {values['prazo_evento']}.\n\n"
            "Apos a analise, restituam-se os autos ou informe-se a providencia "
            "adotada, conforme orientacao superior."
        )
    if tipo == "parte":
        return (
            "PARTE\n\n"
            f"Do: {values['unidade_destino']}\n"
            f"Ao: Senhor {values['destinatario']}\n\n"
            f"Assunto: {values['assunto']} (Ref. SEI: {values['processo_sei']})\n\n"
            f"Comunico a Vossa Senhoria que {values['resumo']}.\n\n"
            f"Providencia sugerida / Adotada: {values['providencia']}.\n"
            f"Prazo/evento: {values['prazo_evento']}.\n\n"
            "Respeitosamente,"
        )
    if tipo == "memorando":
        return (
            "MEMORANDO\n\n"
            f"Processo SEI: {values['processo_sei']}\n"
            f"Assunto: {values['assunto']}\n\n"
            f"A(o) {values['destinatario']},\n\n"
            f"Levo ao conhecimento dessa unidade que {values['resumo']}.\n\n"
            f"Solicito/Sugiro a seguinte providencia: {values['providencia']}.\n"
            f"Prazo/evento estipulado: {values['prazo_evento']}.\n\n"
            "Atenciosamente,"
        )
    if tipo == "portaria":
        return (
            "PORTARIA\n\n"
            f"O COMANDANTE DA {values['unidade_destino']}, no uso de suas atribuicoes legais,\n\n"
            "RESOLVE:\n\n"
            f"Art. 1 - Instaurar procedimento administrativo (Ref. SEI {values['processo_sei']}) "
            f"com a finalidade de apurar fatos relativos a {values['assunto']}.\n\n"
            f"Art. 2 - Designar o {values['destinatario']} para conduzir os trabalhos.\n\n"
            f"Art. 3 - Estabelecer o prazo de {values['prazo_evento']} para a conclusao.\n\n"
            f"Art. 4 - Fica determinado que: {values['providencia']}.\n\n"
            "PUBLIQUE-SE E REGISTRE-SE."
        )
    return (
        "DESPACHO\n\n"
        f"Processo SEI: {values['processo_sei']}\n"
        f"Assunto: {values['assunto']}\n\n"
        "Considerando o teor da demanda em referencia, que trata de "
        f"{values['resumo']}, encaminhe-se a {values['unidade_destino']} "
        "para conhecimento e adocao das providencias cabiveis.\n\n"
        f"Providencia sugerida: {values['providencia']}.\n"
        f"Prazo/evento: {values['prazo_evento']}.\n\n"
        "Apos, retornem os autos para acompanhamento, se necessario."
    )


def _template_values(request: DraftRequest, tipo: str) -> dict[str, str]:
    resumo = _safe_text(request.resumo) or _shorten(request.texto_base) or "[PREENCHER resumo]"
    providencia = request.providencia.strip() or _suggest_providence(tipo, request)
    prazo_evento = " / ".join(
        part for part in [request.prazo.strip(), request.evento.strip()] if part
    )
    return {
        "processo_sei": request.processo_sei.strip() or "[PREENCHER processo SEI]",
        "assunto": request.assunto.strip() or "[PREENCHER assunto]",
        "resumo": resumo,
        "providencia": providencia,
        "unidade_destino": request.unidade_destino.strip()
        or "[PREENCHER unidade/responsavel]",
        "destinatario": request.destinatario.strip()
        or request.unidade_destino.strip()
        or "[PREENCHER destinatario]",
        "prazo_evento": prazo_evento or "[PREENCHER prazo/evento, se aplicavel]",
    }


def _suggest_providence(tipo: str, request: DraftRequest) -> str:
    text = _normalize(" ".join([request.assunto, request.resumo, request.texto_base]))
    if "prazo" in text or request.prazo:
        return "revisar prazo e definir providencia administrativa cabivel"
    if "evento" in text or "reuniao" in text or request.evento:
        return "revisar dados do evento e avaliar comunicacao aos interessados"
    if tipo == "oficio":
        return "responder formalmente apos revisao da autoridade competente"
    if tipo == "informacao":
        return "prestar informacao administrativa para subsidiar decisao"
    if tipo == "parte":
        return "tomar conhecimento dos fatos relatados para fins disciplinares ou operacionais"
    if tipo == "portaria":
        return "conduzir a apuracao de forma isenta dentro do prazo regulamentar"
    if tipo == "memorando":
        return "dar cumprimento as diretrizes internas assinaladas"
    return "encaminhar para conhecimento e providencias cabiveis"


def _missing_fields(request: DraftRequest, tipo: str) -> list[str]:
    missing = []
    if not request.assunto.strip():
        missing.append("assunto")
    if not request.processo_sei.strip():
        missing.append("processo_sei")
    if not (request.resumo.strip() or request.texto_base.strip()):
        missing.append("resumo")
    if tipo in {"despacho", "encaminhamento", "informacao"} and not request.unidade_destino.strip():
        missing.append("unidade_destino")
    if tipo == "oficio" and not (request.destinatario.strip() or request.unidade_destino.strip()):
        missing.append("destinatario")
    return missing


def _used_fields(request: DraftRequest) -> list[str]:
    fields = []
    for name in (
        "processo_sei",
        "assunto",
        "resumo",
        "texto_base",
        "unidade_destino",
        "destinatario",
        "providencia",
        "prazo",
        "evento",
    ):
        value = getattr(request, name)
        if isinstance(value, str) and value.strip():
            fields.append(name)
    return fields


def _confidence(request: DraftRequest, tipo: str, missing: list[str]) -> float:
    score = 0.35
    if tipo in VALID_DRAFT_TYPES:
        score += 0.15
    if request.assunto.strip():
        score += 0.10
    if request.resumo.strip() or request.texto_base.strip():
        score += 0.15
    if request.processo_sei.strip():
        score += 0.05
    if request.unidade_destino.strip() or request.destinatario.strip():
        score += 0.10
    if request.prazo.strip() or request.evento.strip():
        score += 0.05
    score -= min(0.25, len(missing) * 0.05)
    return round(max(0.2, min(score, 0.85)), 2)


def _normalize_type(value: str) -> str:
    normalized = _normalize(value).replace(" ", "_")
    aliases = {
        "despacho_de_encaminhamento": "despacho",
        "despacho": "despacho",
        "oficio": "oficio",
        "oficio_de_resposta": "oficio",
        "informacao": "informacao",
        "comunicacao_interna": "informacao",
        "encaminhamento": "encaminhamento",
        "parte": "parte",
        "parte_diaria": "parte",
        "portaria": "portaria",
        "memorando": "memorando",
    }
    return aliases.get(normalized, "")


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text.strip().lower())


def _safe_text(text: str) -> str:
    return _WHITESPACE.sub(" ", text.strip())


def _shorten(text: str, limit: int = 260) -> str:
    cleaned = _safe_text(text)
    if not cleaned:
        return ""
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3].rstrip()}..."
