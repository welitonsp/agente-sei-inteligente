from typing import Any
from app.intelligence.graph.state import MissionState
from app.intelligence.ai_reasoning import review_minuta, summarize_process
from app.intelligence.local_minutador import DraftRequest, generate_draft
from app.intelligence.local_triage import TriageRequest, analyze_triage

def analyzer_node(state: MissionState) -> dict[str, Any]:
    """Lê o processo e gera o resumo executivo (via camada de IA sob guarda)."""
    # Se ja tem resumo, pula
    if state.get("resumo"):
        return {}

    resumo = summarize_process(state["titulo"], state["texto_original"])
    return {"resumo": resumo}

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
    """Busca contexto institucional (RAG) antes de gerar a minuta."""
    from pathlib import Path
    
    tipo = state.get("tipo_minuta", "").lower()
    contexto = []
    
    # Busca template
    template_path = Path(f"knowledge_base/templates_minutas/{tipo}.md")
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            contexto.append(f"TEMPLATE INSTITUCIONAL ({tipo.upper()}):\n" + f.read())
            
    # Regras adicionais mockadas para Nível 3/4
    contexto.append("DIRETRIZ DE SEGURANÇA: Nenhuma senha ou dado pessoal deve ser exposto na minuta.")
    contexto.append("LEI MILITAR: O tom deve ser formal, respeitoso e hierárquico (Padrão 19 CRPM).")

    # RAG real: inteligência dos manuais (SEI + Redação de Goiás), com fonte.
    from app.intelligence.manual_retriever import retrieve_context

    query = " ".join(
        part
        for part in [state.get("titulo", ""), tipo, state.get("resumo", "")]
        if part
    )
    manual_ctx = retrieve_context(query, k=4)
    if manual_ctx:
        contexto.append(manual_ctx)
    
    return {"contexto_institucional": "\n\n".join(contexto)}

def draft_node(state: MissionState) -> dict[str, Any]:
    """Gera a minuta baseada no contexto."""
    feedback_critico = ""
    if state.get("alertas") and state.get("tentativas_critica", 0) > 0:
        feedback_critico = "\n\nCORRIJA OS SEGUINTES ERROS APONTADOS PELO CRÍTICO:\n" + "\n".join(state["alertas"])

    request = DraftRequest(
        assunto=state["titulo"],
        resumo=state.get("resumo", ""),
        texto_base=state.get("texto_original", "") + "\n" + state.get("contexto_institucional", "") + feedback_critico,
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
    """Critica a minuta gerada contra alucinacoes e violacoes de RAG.

    FAIL-CLOSED: se a auditoria automatica nao estiver disponivel (offline) ou
    falhar, NUNCA declaramos a minuta aprovada — sinalizamos indisponibilidade e
    reforcamos a revisao humana, sem travar o pipeline num loop infinito.
    """
    tentativas = state.get("tentativas_critica", 0) + 1

    verdict = review_minuta(
        texto_base=state.get("texto_original", ""),
        minuta_gerada=state.get("minuta_texto", ""),
        contexto=state.get("contexto_institucional", ""),
    )

    if not verdict.disponivel:
        return {
            "status": "pronto_para_revisao",
            "tentativas_critica": tentativas,
            "revisao_humana_obrigatoria": True,
            "alertas": [
                "AVISO: auditoria automatica de IA indisponivel — revisao "
                f"humana reforcada. {verdict.feedback}"
            ],
        }

    if not verdict.aprovado and tentativas < 3:
        # Reprova e devolve para o draft_node
        return {
            "status": "rejeitado_pelo_critico",
            "tentativas_critica": tentativas,
            "alertas": [f"TENTATIVA {tentativas}: {verdict.feedback}"],
        }

    return {
        "status": "pronto_para_revisao",
        "tentativas_critica": tentativas,
        "revisao_humana_obrigatoria": True,
        "alertas": (
            ["Auditoria de IA: Minuta Aprovada"]
            if verdict.aprovado
            else [
                "AVISO: Aprovado com ressalvas apos 3 tentativas. "
                f"Erro: {verdict.feedback}"
            ]
        ),
    }

def audit_node(state: MissionState) -> dict[str, Any]:
    """Persiste o estado final para rastreabilidade real (auditoria)."""
    import logging
    from datetime import datetime, timezone

    from app.core import audit

    try:
        audit_id = audit.record(
            action="MISSAO_GRAFO_CONCLUIDA",
            result=state.get("status", "desconhecido"),
            actor_id=state.get("usuario_local") or None,
            target_type="processo_sei",
            target_id=state.get("processo_sei") or None,
            reason="Fluxo cognitivo LangGraph concluido; revisao humana obrigatoria.",
            metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "unidade_destino": state.get("unidade_destino"),
                "tipo_minuta": state.get("tipo_minuta"),
                "tentativas_critica": state.get("tentativas_critica"),
                "revisao_humana_obrigatoria": state.get(
                    "revisao_humana_obrigatoria", True
                ),
                "texto_integral_persistido": False,
            },
        )
        return {"alertas": [f"Auditoria registrada (id={audit_id})."]}
    except Exception as exc:  # auditoria nunca deve derrubar o fluxo
        logging.getLogger("agente19.audit").warning(
            "Falha ao persistir auditoria do grafo: %s", exc
        )
        return {"alertas": [f"AVISO: auditoria nao persistida ({exc})."]}
