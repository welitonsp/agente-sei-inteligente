from typing import Any

from app.intake.manual_text import ManualTextRequest
from app.intelligence.graph.state import MissionState
from app.intelligence.llm_gemini import analyze_with_gemini, review_with_gemini
from app.intelligence.local_minutador import DraftRequest, generate_draft
from app.intelligence.local_triage import TriageRequest, analyze_triage


def analyzer_node(state: MissionState) -> dict[str, Any]:
    """Le o processo e gera o resumo executivo."""
    if state.get("resumo"):
        return {}

    request = ManualTextRequest(
        titulo=state["titulo"],
        texto=state["texto_original"],
        processo_sei=state["processo_sei"],
        usuario_local=state["usuario_local"],
        estacao="",
        origem="langgraph",
    )
    result = analyze_with_gemini(request)
    return {"resumo": result.resumo_executivo}


def triage_node(state: MissionState) -> dict[str, Any]:
    """Define a unidade de destino e o tipo de minuta se nao fornecidos."""
    if state.get("unidade_destino") and state.get("tipo_minuta"):
        return {}

    request = TriageRequest(
        assunto=state["titulo"],
        texto=state.get("resumo") or state["texto_original"],
        processo_sei=state["processo_sei"],
        usuario_local=state["usuario_local"],
        estacao="",
        origem="langgraph",
    )
    result = analyze_triage(request)

    updates = {}
    if not state.get("unidade_destino") and result.unidade_sugerida:
        updates["unidade_destino"] = result.unidade_sugerida
    if not state.get("tipo_minuta") and result.tipo_minuta_sugerido:
        updates["tipo_minuta"] = result.tipo_minuta_sugerido

    return updates


def checklist_node(state: MissionState) -> dict[str, Any]:
    """Verifica se todos os campos para a minuta estao presentes."""
    pendentes = []
    if not state.get("processo_sei"):
        pendentes.append("processo_sei")
    if not state.get("unidade_destino"):
        pendentes.append("unidade_destino")
    if not state.get("tipo_minuta"):
        pendentes.append("tipo_minuta")
    if not state.get("texto_original") and not state.get("resumo"):
        pendentes.append("texto")

    status = "precisa_complemento" if pendentes else "pronto_para_rag"
    return {"campos_pendentes": pendentes, "status": status}


def rag_node(state: MissionState) -> dict[str, Any]:
    """Busca contexto institucional antes de gerar a minuta."""
    from pathlib import Path

    tipo = state.get("tipo_minuta", "").lower()
    contexto = []

    template_path = Path(f"knowledge_base/templates_minutas/{tipo}.md")
    if template_path.exists():
        with open(template_path, encoding="utf-8") as file:
            contexto.append(f"TEMPLATE INSTITUCIONAL ({tipo.upper()}):\n" + file.read())

    contexto.append(
        "DIRETRIZ DE SEGURANCA: Nenhuma senha ou dado pessoal deve ser exposto na minuta."
    )
    contexto.append(
        "LEI MILITAR: O tom deve ser formal, respeitoso e hierarquico (Padrao 19 CRPM)."
    )

    return {"contexto_institucional": "\n\n".join(contexto)}


def draft_node(state: MissionState) -> dict[str, Any]:
    """Gera a minuta baseada no contexto."""
    feedback_critico = ""
    if state.get("alertas") and state.get("tentativas_critica", 0) > 0:
        feedback_critico = "\n\nCORRIJA OS SEGUINTES ERROS APONTADOS PELO CRITICO:\n" + "\n".join(
            state["alertas"]
        )

    request = DraftRequest(
        assunto=state["titulo"],
        resumo=state.get("resumo", ""),
        texto_base=state.get("texto_original", "")
        + "\n"
        + state.get("contexto_institucional", "")
        + feedback_critico,
        processo_sei=state["processo_sei"],
        tipo_minuta=state["tipo_minuta"],
        unidade_destino=state["unidade_destino"],
        destinatario=state["unidade_destino"],
        providencia="",
        prazo="",
        evento="",
        usuario_local=state["usuario_local"],
        estacao="",
        origem="langgraph",
    )
    result = generate_draft(request)
    return {
        "minuta_texto": result.texto,
        "alertas": result.alertas,
        "status": "minuta_gerada",
    }


def critic_node(state: MissionState) -> dict[str, Any]:
    """Critica a minuta gerada para reduzir alucinacoes e violacoes de RAG."""
    tentativas = state.get("tentativas_critica", 0) + 1

    avaliacao = review_with_gemini(
        texto_base=state.get("texto_original", ""),
        minuta_gerada=state.get("minuta_texto", ""),
        contexto=state.get("contexto_institucional", ""),
    )

    if not avaliacao["aprovado"] and tentativas < 3:
        return {
            "status": "rejeitado_pelo_critico",
            "tentativas_critica": tentativas,
            "alertas": [f"TENTATIVA {tentativas}: {avaliacao['feedback']}"],
        }

    alertas = (
        ["Auditoria de IA: Minuta Aprovada"]
        if avaliacao["aprovado"]
        else [f"AVISO: Aprovado com ressalvas apos 3 tentativas. Erro: {avaliacao['feedback']}"]
    )
    return {
        "status": "pronto_para_revisao",
        "tentativas_critica": tentativas,
        "revisao_humana_obrigatoria": True,
        "alertas": alertas,
    }


def audit_node(state: MissionState) -> dict[str, Any]:
    """Salva o estado final para rastreabilidade e auditoria."""
    import json

    log_data = {
        "timestamp": "now",
        "processo_sei": state.get("processo_sei"),
        "usuario_local": state.get("usuario_local"),
        "unidade_destino": state.get("unidade_destino"),
        "tipo_minuta": state.get("tipo_minuta"),
        "status_final": state.get("status"),
        "tentativas_critica": state.get("tentativas_critica"),
        "revisao_humana_obrigatoria": state.get("revisao_humana_obrigatoria"),
    }

    print(
        "\n=== LOG DE AUDITORIA DO AGENTE 19 ===\n"
        f"{json.dumps(log_data, indent=2)}"
        "\n======================================\n"
    )

    return {}
