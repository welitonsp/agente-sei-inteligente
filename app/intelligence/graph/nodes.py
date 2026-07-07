from typing import Any
from app.intelligence.graph.state import MissionState
from app.intelligence.llm_gemini import analyze_with_gemini
from app.intake.manual_text import ManualTextRequest
from app.intelligence.local_minutador import DraftRequest, generate_draft
from app.intelligence.local_triage import TriageRequest, analyze_triage

def analyzer_node(state: MissionState) -> dict[str, Any]:
    """Lê o processo e gera o resumo executivo."""
    # Se ja tem resumo, pula
    if state.get("resumo"):
        return {}
        
    request = ManualTextRequest(
        titulo=state["titulo"],
        texto=state["texto_original"],
        processo_sei=state["processo_sei"],
        usuario_local=state["usuario_local"],
        estacao="",
        origem="langgraph"
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
        origem="langgraph"
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
    if not state.get("processo_sei"): pendentes.append("processo_sei")
    if not state.get("unidade_destino"): pendentes.append("unidade_destino")
    if not state.get("tipo_minuta"): pendentes.append("tipo_minuta")
    if not state.get("texto_original") and not state.get("resumo"): pendentes.append("texto")
    
    status = "precisa_complemento" if pendentes else "pronto_para_minuta"
    return {"campos_pendentes": pendentes, "status": status}

def draft_node(state: MissionState) -> dict[str, Any]:
    """Gera a minuta baseada no contexto."""
    request = DraftRequest(
        assunto=state["titulo"],
        resumo=state.get("resumo", ""),
        texto_base=state["texto_original"],
        processo_sei=state["processo_sei"],
        tipo_minuta=state["tipo_minuta"],
        unidade_destino=state["unidade_destino"],
        destinatario=state["unidade_destino"],
        providencia="",
        prazo="",
        evento="",
        usuario_local=state["usuario_local"],
        estacao="",
        origem="langgraph"
    )
    result = generate_draft(request)
    return {
        "minuta_texto": result.texto,
        "alertas": result.alertas,
        "status": "minuta_gerada"
    }

def critic_node(state: MissionState) -> dict[str, Any]:
    """Critica a minuta gerada para garantir que nao ha alucinacoes (Stub)."""
    # Exemplo: O critico verifica regras do GOIAS.
    tentativas = state.get("tentativas_critica", 0) + 1
    
    if "ALUCINACAO" in state.get("minuta_texto", "") and tentativas < 3:
        return {"status": "rejeitado_pelo_critico", "tentativas_critica": tentativas}
        
    return {"status": "pronto_para_revisao", "tentativas_critica": tentativas, "revisao_humana_obrigatoria": True}
