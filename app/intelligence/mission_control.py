"""Orquestrador operacional do Agente 19.

Esta camada junta analise, triagem, minutador e Control Plane em um contrato
unico para revisao humana. Ela nao executa ato oficial, nao escreve no SEI e
nao substitui as barreiras individuais dos subagentes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from app.agent.control_plane import (
    build_action_proposal,
    build_supervised_mission,
    evaluate_action_proposal,
    new_mission_id,
)
from app.intelligence.local_minutador import DraftRequest, generate_draft
from app.intelligence.local_triage import TriageRequest, analyze_triage


OFFICIAL_ACTIONS_BLOCKED = [
    "ASSINAR_DOCUMENTO",
    "ENVIAR_PROCESSO",
    "TRAMITAR_PROCESSO",
    "CONCLUIR_PROCESSO",
    "DAR_CIENCIA_AUTOMATICA",
    "EXCLUIR_DOCUMENTO",
    "CANCELAR_DOCUMENTO",
    "ALTERAR_SIGILO_ACESSO",
    "CONCEDER_CREDENCIAL",
    "LIBERAR_ACESSO_EXTERNO",
]


@dataclass(frozen=True)
class MissionRequest:
    titulo: str
    texto: str
    processo_sei: str = ""
    usuario_local: str = ""
    estacao: str = ""
    unidade_destino: str = ""
    tipo_minuta: str = ""
    origem: str = "mission_control"
    mission_trace_id: str = ""


@dataclass(frozen=True)
class MissionResult:
    status: str
    prontidao_operacional: float
    etapa_recomendada: str
    plano_operacional: list[str]
    riscos: list[str]
    analise: dict[str, Any]
    triagem: dict[str, Any]
    minuta: dict[str, Any]
    campos_pendentes: list[str]
    revisao_humana_obrigatoria: bool = True
    audit_log_ids: list[int] = field(default_factory=list)
    mission_trace_id: str = ""
    mission_id: str = ""
    control_plane: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mission_id": self.mission_id,
            "mission_trace_id": self.mission_trace_id,
            "resultado": {
                "prontidao_operacional": self.prontidao_operacional,
                "etapa_recomendada": self.etapa_recomendada,
                "plano_operacional": self.plano_operacional,
                "riscos": self.riscos,
                "analise": self.analise,
                "triagem": self.triagem,
                "minuta": self.minuta,
                "control_plane": self.control_plane,
            },
            "confianca": self.prontidao_operacional,
            "fontes": [
                "analise_local",
                "triagem_local",
                "minutador_local",
                "control_plane",
            ],
            "campos_pendentes": self.campos_pendentes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_sugeridas": [
                "REVISAR_RESUMO",
                "REVISAR_TRIAGEM",
                "REVISAR_MINUTA",
                "COPIAR_MINUTA",
            ],
            "acoes_bloqueadas": OFFICIAL_ACTIONS_BLOCKED,
            "logs": self.audit_log_ids,
        }


AnalyzeFn = Callable[[str], dict[str, Any]]
TriageFn = Callable[[TriageRequest], Any]
DraftFn = Callable[[DraftRequest], Any]


_DEADLINE_RE = re.compile(
    r"(?P<prazo>\b\d{1,3}\s+(?:dias|dia|horas|hora)\s+(?:uteis|corridos)?\b)",
    re.IGNORECASE,
)


def execute_mission(
    request: MissionRequest,
    *,
    analisar: AnalyzeFn | None = None,
    triar: TriageFn | None = None,
    minutador: DraftFn | None = None,
) -> MissionResult:
    """Executa a missao supervisionada com guard central e sem ato oficial."""
    texto = request.texto.strip()
    titulo = request.titulo.strip()
    mission_id = new_mission_id()
    if not (texto or titulo):
        return _empty_result(["titulo", "texto"], request.mission_trace_id, mission_id)

    analise = (analisar or _basic_analysis)("\n".join([titulo, texto]))
    triage_contract = _as_contract(
        (triar or analyze_triage)(
            TriageRequest(
                assunto=titulo,
                texto=texto,
                processo_sei=request.processo_sei,
                usuario_local=request.usuario_local,
                estacao=request.estacao,
                origem=request.origem,
            )
        )
    )
    triagem = _flatten_result(triage_contract)
    draft_contract = _as_contract(
        (minutador or generate_draft)(
            DraftRequest(
                assunto=titulo or analise.get("tipo_provavel", "demanda"),
                resumo=analise.get("resumo_curto", ""),
                texto_base=texto,
                processo_sei=request.processo_sei,
                tipo_minuta=request.tipo_minuta
                or triagem.get("tipo_minuta_sugerido", ""),
                unidade_destino=request.unidade_destino
                or triagem.get("unidade_sugerida", ""),
                destinatario=request.unidade_destino
                or triagem.get("unidade_sugerida", ""),
                providencia=analise.get("providencia_sugerida", "")
                or triagem.get("providencia_sugerida", ""),
                prazo=_first_deadline(analise),
                usuario_local=request.usuario_local,
                estacao=request.estacao,
                origem=request.origem,
            )
        )
    )
    minuta = _flatten_result(draft_contract)
    pending = _pending_fields(request, triage_contract, draft_contract)
    risks = _risk_markers(analise, triage_contract, draft_contract, pending)
    readiness = _readiness_score(request, analise, triage_contract, draft_contract, pending)
    etapa = _recommended_step(pending, draft_contract, readiness)
    ready = not pending and bool(minuta.get("texto")) and readiness >= 0.7
    status = "pronto_para_revisao" if ready else "precisa_complemento"
    plan = _mission_plan(etapa, bool(request.unidade_destino), bool(_first_deadline(analise)))

    proposal = build_action_proposal(
        mission_id=mission_id,
        tool_name="mission_control",
        action="GERAR_MINUTA",
        title="Preparar pacote de revisao humana",
        rationale="Gerar rascunho local e pacote de decisao, sem escrita no SEI.",
        metadata={
            "processo_sei": request.processo_sei,
            "texto_integral_persistido": False,
            "tipo_minuta": minuta.get("tipo_minuta", ""),
        },
    )
    decision = evaluate_action_proposal(
        proposal,
        usuario_local=request.usuario_local,
        processo_sei=request.processo_sei,
    )
    control_plane = build_supervised_mission(
        mission_id=mission_id,
        title=titulo or "Missao Agente 19",
        proposals=[proposal],
        decisions=[decision],
        ready=ready,
    ).to_contract()

    return MissionResult(
        status=status,
        prontidao_operacional=readiness,
        etapa_recomendada=etapa,
        plano_operacional=plan,
        riscos=risks,
        analise=analise,
        triagem=triagem,
        minuta=minuta,
        campos_pendentes=pending,
        audit_log_ids=_log_ids(triage_contract, draft_contract),
        mission_trace_id=request.mission_trace_id,
        mission_id=mission_id,
        control_plane=control_plane,
    )


def _empty_result(
    pending: list[str], mission_trace_id: str = "", mission_id: str = ""
) -> MissionResult:
    return MissionResult(
        status="precisa_complemento",
        prontidao_operacional=0.0,
        etapa_recomendada="informar_conteudo",
        plano_operacional=["Informar titulo e texto/documento antes da analise."],
        riscos=["conteudo_ausente"],
        analise={},
        triagem={},
        minuta={},
        campos_pendentes=pending,
        mission_trace_id=mission_trace_id,
        mission_id=mission_id,
    )


def _basic_analysis(text: str) -> dict[str, Any]:
    normalized = " ".join(text.split())
    lowered = normalized.lower()
    tipo = "despacho"
    if "oficio" in lowered or "ofício" in lowered:
        tipo = "oficio"
    elif "informacao" in lowered or "informação" in lowered:
        tipo = "informacao"
    elif "convocacao" in lowered or "convocação" in lowered:
        tipo = "convocacao"
    elif "portaria" in lowered:
        tipo = "portaria"

    deadline_match = _DEADLINE_RE.search(normalized)
    prazo = deadline_match.group("prazo") if deadline_match else ""
    providencia = "Revisar manualmente e submeter a autoridade competente."
    if "apoio" in lowered:
        providencia = "Analisar solicitacao de apoio e definir providencia cabivel."
    elif "prazo" in lowered or prazo:
        providencia = "Registrar prazo e acompanhar resposta manualmente."

    return {
        "tipo_provavel": tipo,
        "resumo_curto": _shorten(normalized),
        "providencia_sugerida": providencia,
        "prazos": [{"descricao": prazo, "data_limite": prazo}] if prazo else [],
        "prazo_detectado": prazo,
        "confianca": 0.74 if normalized else 0.0,
        "resumo_fonte": "local",
    }


def _shorten(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _as_contract(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_contract"):
        return value.to_contract()
    return value if isinstance(value, dict) else {}


def _flatten_result(contract: dict[str, Any]) -> dict[str, Any]:
    result = contract.get("resultado")
    if isinstance(result, dict):
        return result
    return contract


def _first_deadline(analise: dict[str, Any]) -> str:
    prazos = analise.get("prazos") or []
    if not isinstance(prazos, list) or not prazos:
        return ""
    first = prazos[0]
    if not isinstance(first, dict):
        return ""
    return str(first.get("data_limite") or first.get("descricao") or "").strip()


def _pending_fields(
    request: MissionRequest, triagem: dict[str, Any], minuta: dict[str, Any]
) -> list[str]:
    pending = []
    if not request.processo_sei.strip():
        pending.append("processo_sei")
    if not request.unidade_destino.strip():
        pending.append("unidade_destino")
    for value in triagem.get("campos_pendentes", []) or []:
        field = str(value)
        if _field_resolved_by_request(field, request):
            continue
        pending.append(field)
    for value in minuta.get("campos_pendentes", []) or []:
        field = str(value)
        if _field_resolved_by_request(field, request):
            continue
        pending.append(field)
    return sorted(set(pending))


def _field_resolved_by_request(field: str, request: MissionRequest) -> bool:
    if field in {"unidade_destino", "destinatario", "knowledge_base_regras"}:
        return bool(request.unidade_destino.strip())
    if field == "processo_sei":
        return bool(request.processo_sei.strip())
    if field in {"regra_direcionamento"}:
        return bool(request.unidade_destino.strip())
    return False


def _risk_markers(
    analise: dict[str, Any],
    triagem: dict[str, Any],
    minuta: dict[str, Any],
    pending: list[str],
) -> list[str]:
    risks = ["atos_oficiais_bloqueados"]
    if pending:
        risks.append("campos_pendentes")
    if float(analise.get("confianca", 0.0) or 0.0) < 0.7:
        risks.append("baixa_confianca_analise")
    if float(triagem.get("confianca", 0.0) or 0.0) < 0.7:
        risks.append("triagem_exige_revisao")
    if float(minuta.get("confianca", 0.0) or 0.0) < 0.7:
        risks.append("minuta_exige_revisao")
    if analise.get("resumo_fonte") == "local":
        risks.append("resumo_sem_ia_externa")
    return sorted(set(risks))


def _readiness_score(
    request: MissionRequest,
    analise: dict[str, Any],
    triagem: dict[str, Any],
    minuta: dict[str, Any],
    pending: list[str],
) -> float:
    score = 0.25
    if request.texto.strip():
        score += 0.15
    if request.processo_sei.strip():
        score += 0.10
    if analise.get("resumo_curto"):
        score += 0.15
    if analise.get("prazos") or analise.get("prazo_detectado"):
        score += 0.08
    triage_result = _flatten_result(triagem)
    if request.unidade_destino.strip() or triage_result.get("unidade_sugerida"):
        score += 0.12
    draft_result = _flatten_result(minuta)
    if draft_result.get("texto"):
        score += 0.15
    score -= min(0.25, len(pending) * 0.05)
    return round(max(0.0, min(score, 0.9)), 2)


def _recommended_step(
    pending: list[str], minuta: dict[str, Any], prontidao: float
) -> str:
    if "texto" in pending or "titulo" in pending:
        return "informar_conteudo"
    if "unidade_destino" in pending or "destinatario" in pending:
        return "definir_unidade_destino"
    draft_result = _flatten_result(minuta)
    if not draft_result.get("texto"):
        return "gerar_minuta"
    if prontidao < 0.7:
        return "completar_campos_e_revisar"
    return "revisar_minuta_com_humano"


def _mission_plan(etapa: str, has_unit: bool, has_deadline: bool) -> list[str]:
    plan = ["Conferir resumo e fontes antes de usar qualquer texto."]
    if not has_unit:
        plan.append("Definir unidade/destinatario com responsavel humano.")
    else:
        plan.append("Validar se a unidade sugerida esta correta para o caso.")
    if has_deadline:
        plan.append("Conferir prazo identificado e registrar acompanhamento manual.")
    plan.append("Revisar minuta local, corrigir campos pendentes e copiar manualmente.")
    plan.append("Manter assinatura, envio, tramitacao e conclusao fora do agente.")
    if etapa != "revisar_minuta_com_humano":
        plan.append(f"Etapa imediata: {etapa}.")
    return plan


def _log_ids(*contracts: dict[str, Any]) -> list[int]:
    ids: list[int] = []
    for contract in contracts:
        for value in contract.get("logs", []) or []:
            try:
                ids.append(int(value))
            except (TypeError, ValueError):
                continue
    return ids
