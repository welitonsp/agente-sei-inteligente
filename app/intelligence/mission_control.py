"""Orquestrador operacional do Agente 19.

Esta camada junta analise, triagem e minutador em um contrato unico para
revisao humana. Ela nao executa ato oficial, nao escreve no SEI e nao substitui
as barreiras individuais dos subagentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from app.intelligence.local_minutador import DraftRequest
from app.intelligence.local_triage import TriageRequest
from app.intelligence.swarm import SwarmCoordinator


OFFICIAL_ACTIONS_BLOCKED = [
    "ASSINAR_DOCUMENTO",
    "ENVIAR_PROCESSO",
    "TRAMITAR_PROCESSO",
    "CONCLUIR_PROCESSO",
    "DAR_CIENCIA_AUTOMATICA",
    "EXCLUIR_DOCUMENTO",
    "CANCELAR_DOCUMENTO",
    "ALTERAR_SIGILO_ACESSO",
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

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mission_trace_id": self.mission_trace_id,
            "resultado": {
                "prontidao_operacional": self.prontidao_operacional,
                "etapa_recomendada": self.etapa_recomendada,
                "plano_operacional": self.plano_operacional,
                "riscos": self.riscos,
                "analise": self.analise,
                "triagem": self.triagem,
                "minuta": self.minuta,
            },
            "confianca": self.prontidao_operacional,
            "fontes": ["analise_local", "triagem_local", "minutador_local"],
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



def execute_mission(
    request: MissionRequest,
    *,
    analisar: AnalyzeFn | None = None,
    triar: TriageFn | None = None,
    minutador: DraftFn | None = None,
) -> MissionResult:
    """Executa a missao supervisionada usando o Enxame (Swarm Multi-Agente)."""
    texto = request.texto.strip()
    titulo = request.titulo.strip()
    if not (texto or titulo):
        return _empty_result(["titulo", "texto"], request.mission_trace_id)

    # Iniciar Enxame
    coordinator = SwarmCoordinator()
    state = coordinator.run(
        processo_sei=request.processo_sei,
        titulo=titulo,
        texto=texto,
        usuario=request.usuario_local
    )

    prontidao = 0.90 if state.aprovado_pelo_critico else 0.50
    status = "pronto_para_revisao" if state.aprovado_pelo_critico else "precisa_complemento"
    etapa = "revisar_minuta_com_humano" if state.aprovado_pelo_critico else "completar_campos_e_revisar"
    
    plan = [
        "Enxame concluiu a orquestração.",
        f"Iterações do redator: {state.tentativas_redacao}"
    ]
    if not state.aprovado_pelo_critico:
        plan.append("O Agente Crítico rejeitou a minuta. Revisão humana estrita é necessária.")

    return MissionResult(
        status=status,
        prontidao_operacional=prontidao,
        etapa_recomendada=etapa,
        plano_operacional=plan,
        riscos=["revisao_critica_reprovou"] if not state.aprovado_pelo_critico else [],
        analise={"resumo_curto": state.resumo, "providencia_sugerida": state.providencia_sugerida, "tipo_provavel": state.intencao_detectada},
        triagem={"unidade_sugerida": "PM/19 CRPM", "interesse_19crpm": state.intencao_detectada},
        minuta={"texto": state.minuta_rascunho, "tipo_minuta": state.tipo_minuta},
        campos_pendentes=[],
        audit_log_ids=[],
        mission_trace_id=request.mission_trace_id,
    )


def _empty_result(pending: list[str], mission_trace_id: str = "") -> MissionResult:
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
    )


def _as_contract(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_contract"):
        return value.to_contract()
    return value if isinstance(value, dict) else {}


def _first_deadline(analise: dict[str, Any]) -> str:
    prazos = analise.get("prazos") or []
    if not isinstance(prazos, list) or not prazos:
        return ""
    first = prazos[0]
    if not isinstance(first, dict):
        return ""
    return str(first.get("data_limite") or first.get("descricao") or "").strip()


def _draft_type_from_analysis(analise: dict[str, Any]) -> str:
    tipo = str(analise.get("tipo_provavel", "")).strip().lower()
    if tipo in {"oficio", "informacao", "encaminhamento", "despacho"}:
        return tipo
    if tipo in {"requisicao", "convocacao"}:
        return "oficio"
    return "despacho"


def _pending_fields(
    request: MissionRequest, triagem: dict[str, Any], minuta: dict[str, Any]
) -> list[str]:
    pending = []
    if not request.processo_sei.strip():
        pending.append("processo_sei")
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
    if field in {"unidade_destino", "destinatario"}:
        return bool(request.unidade_destino.strip())
    if field == "knowledge_base_regras":
        return bool(request.unidade_destino.strip())
    if field == "processo_sei":
        return bool(request.processo_sei.strip())
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
    if (analise.get("prazos") or analise.get("prazo_detectado")):
        score += 0.08
    if request.unidade_destino.strip() or triagem.get("resultado", {}).get(
        "unidade_sugerida"
    ):
        score += 0.12
    if minuta.get("resultado", {}).get("texto"):
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
    if not minuta.get("resultado", {}).get("texto"):
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
