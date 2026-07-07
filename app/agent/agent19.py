"""Nucleo explicito do Agente 19.

O Agente 19 nao e apenas um endpoint de analise. Ele percebe uma solicitacao,
classifica a intencao, escolhe uma ferramenta permitida, executa a missao
supervisionada e devolve uma resposta com plano, limites e auditoria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agent.tools import get_agent_tool, list_agent_tools
from app.agent.tracing import AgentTrace, start_agent_trace
from app.intelligence.mission_control import (
    OFFICIAL_ACTIONS_BLOCKED,
    MissionRequest,
    execute_mission,
)
from app.intelligence.ai_provider import AIRole, get_ai_provider
from app.evaluation.shadow_mode import ShadowModeLogger


AGENT_NAME = "Agente 19"
AGENT_KIND = "servidor_digital_ia_supervisionado"


@dataclass(frozen=True)
class AgentRequest:
    mensagem: str
    texto: str = ""
    titulo: str = ""
    processo_sei: str = ""
    usuario_local: str = ""
    perfil_local: str = ""
    unidade_destino: str = "PM/19 CRPM"
    origem: str = "agent19"
    trace_id: str = ""


@dataclass(frozen=True)
class AgentToolCall:
    ferramenta: str
    status: str
    motivo: str
    permissao: str = ""
    read_only: bool = True

    def to_contract(self) -> dict[str, object]:
        return {
            "ferramenta": self.ferramenta,
            "status": self.status,
            "motivo": self.motivo,
            "permissao": self.permissao,
            "read_only": self.read_only,
        }


@dataclass(frozen=True)
class AgentResult:
    status: str
    intencao: str
    resposta: str
    plano: list[str]
    ferramentas_usadas: list[AgentToolCall]
    missao: dict[str, Any]
    trace: AgentTrace
    revisao_humana_obrigatoria: bool = True
    acoes_bloqueadas: list[str] = field(
        default_factory=lambda: list(OFFICIAL_ACTIONS_BLOCKED)
    )

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "agente": {
                "nome": AGENT_NAME,
                "tipo": AGENT_KIND,
                "intencao": self.intencao,
            },
            "resposta": self.resposta,
            "plano": self.plano,
            "ferramentas_disponiveis": list_agent_tools(),
            "ferramentas_usadas": [
                tool.to_contract() for tool in self.ferramentas_usadas
            ],
            "trace": self.trace.to_contract(),
            "resultado": self.missao,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_bloqueadas": self.acoes_bloqueadas,
        }


def run_agent19(request: AgentRequest) -> AgentResult:
    trace = start_agent_trace(request.trace_id).add(
        "receber_solicitacao", "ok", "Solicitacao recebida pelo nucleo do agente."
    )
    intencao = _detect_intent(request.mensagem)
    trace = trace.add("detectar_intencao", "ok", intencao)
    plano = _plan_for_intent(intencao)
    trace = trace.add("montar_plano", "ok", "Plano operacional supervisionado criado.")

    if not (request.texto.strip() or request.titulo.strip()):
        trace = trace.add("verificar_contexto", "pendente", "Texto ou titulo ausente.")
        return AgentResult(
            status="precisa_complemento",
            intencao=intencao,
            resposta=(
                "Sou o Agente 19. Para agir como servidor digital, preciso do "
                "texto visivel, texto selecionado ou PDF exportado manualmente."
            ),
            plano=plano,
            ferramentas_usadas=[],
            missao={},
            trace=trace,
        )

    tool = get_agent_tool("mission_control")
    trace = trace.add(
        "selecionar_ferramenta",
        "ok",
        f"{tool.nome}:{tool.permissao}",
    )
    mission = execute_mission(
        MissionRequest(
            titulo=request.titulo or "Processo SEI",
            texto=request.texto,
            processo_sei=request.processo_sei,
            usuario_local=request.usuario_local,
            unidade_destino=request.unidade_destino,
            origem=request.origem,
            mission_trace_id=trace.trace_id,
        )
    ).to_contract()
    trace = trace.add(
        "executar_ferramenta",
        mission.get("status", "ok"),
        "mission_control executado sem acao oficial.",
    )
    trace = trace.add("montar_resposta", "ok", "Resposta final preparada para revisao humana.")

    # Shadow Mode: gravar a proposta de acao que seria tomada
    try:
        logger = ShadowModeLogger()
        raw_conf = str(mission.get("confianca", "0.0") or "0.0")
        confidence = float(raw_conf.replace("%", ""))
        acao_proposta = "analisar_e_alertar" if "precisa_revisao" in mission.get("status", "") else "executar_proximo_passo"
        logger.record_proposal(
            trace_id=trace.trace_id,
            processo=request.processo_sei,
            intencao=intencao,
            acao_proposta=acao_proposta,
            confidence=confidence,
        )
    except Exception as e:
        trace = trace.add("shadow_mode_error", "erro_interno", str(e))

    return AgentResult(
        status=mission.get("status", "precisa_revisao"),
        intencao=intencao,
        resposta=_build_response(request, mission),
        plano=plano,
        ferramentas_usadas=[
            AgentToolCall(
                ferramenta=tool.nome,
                status="executada",
                motivo="Analisar processo aberto e filtrar interesse do 19 CRPM.",
                permissao=tool.permissao,
                read_only=tool.read_only,
            )
        ],
        missao=mission,
        trace=trace,
    )


def _detect_intent(message: str) -> str:
    # Fallback heuristico seguro em caso de falha de rede/quota/offline
    fallback = "analisar_processo"
    text_lower = " ".join(message.lower().split())
    if "19" in text_lower or "interesse" in text_lower or "crpm" in text_lower:
        fallback = "analisar_interesse_19crpm"
    elif "minuta" in text_lower or "despacho" in text_lower or "oficio" in text_lower:
        fallback = "preparar_minuta"
    elif "prazo" in text_lower:
        fallback = "identificar_prazo"

    provider = get_ai_provider()
    if not provider.is_real:
        return fallback

    prompt = (
        f"Classifique a intenção do usuário em UMA das opções exatas: "
        f"[analisar_interesse_19crpm, preparar_minuta, identificar_prazo, analisar_processo].\n"
        f"Mensagem original: '{message}'\n"
        f"Apenas responda com a opção escolhida, sem pontuação ou texto adicional."
    )
    
    try:
        completion = provider.complete(AIRole.CLASSIFICACAO, prompt)
        text = completion.text.strip().lower()
        if "19crpm" in text or "interesse" in text:
            return "analisar_interesse_19crpm"
        if "minuta" in text:
            return "preparar_minuta"
        if "prazo" in text:
            return "identificar_prazo"
        return "analisar_processo"
    except Exception:
        return fallback


def _plan_for_intent(intent: str) -> list[str]:
    return [
        "Ler somente conteudo visivel, selecionado ou enviado pelo usuario.",
        "Identificar assunto, prazo, providencia e possivel interesse do 19 CRPM.",
        "Usar ferramenta segura de missao supervisionada.",
        "Apresentar riscos, pendencias e rascunho externo quando aplicavel.",
        "Manter atos oficiais bloqueados e revisao humana obrigatoria.",
    ]


def _build_response(request: AgentRequest, mission: dict[str, Any]) -> str:
    result = mission.get("resultado", {}) if isinstance(mission, dict) else {}
    analysis = result.get("analise", {}) if isinstance(result, dict) else {}
    triage = result.get("triagem", {}) if isinstance(result, dict) else {}
    readiness = result.get("prontidao_operacional", mission.get("confianca", ""))
    pending = ", ".join(mission.get("campos_pendentes", []) or []) or "nenhuma"
    risks = ", ".join(result.get("riscos", []) or []) or "nenhum"
    process = request.processo_sei or "nao identificado"
    interest = triage.get("interesse_19crpm") or "a confirmar pelo 19 CRPM"
    unidade = triage.get("unidade_sugerida") or "a confirmar"
    regra = triage.get("regra_aplicada") or "sem regra conclusiva"
    evidencias = ", ".join(triage.get("evidencias", []) or []) or "sem evidencia configurada"

    return "\n".join(
        [
            f"Processo: {process}",
            f"Interesse 19 CRPM: {interest}",
            f"Unidade sugerida: {unidade}",
            f"Regra aplicada: {regra}",
            f"Evidencias: {evidencias}",
            f"Tipo/assunto: {analysis.get('tipo_provavel', 'nao classificado')}",
            f"Resumo: {analysis.get('resumo_curto', 'resumo nao gerado')}",
            f"Providencia: {analysis.get('providencia_sugerida') or triage.get('providencia_sugerida') or 'revisar manualmente'}",
            f"Prontidao: {readiness}",
            f"Riscos: {risks}",
            f"Pendencias: {pending}",
            "Limite: eu preparo e oriento; o humano revisa e pratica qualquer ato oficial.",
        ]
    )
