from langgraph.graph import StateGraph, END
from app.intelligence.graph.state import MissionState
from app.intelligence.graph.nodes import (
    analyzer_node, triage_node, checklist_node, draft_node, critic_node
)

def route_after_checklist(state: MissionState) -> str:
    if state.get("status") == "precisa_complemento":
        return END
    return "draft"

def route_after_critic(state: MissionState) -> str:
    if state.get("status") == "rejeitado_pelo_critico":
        return "draft"
    return END

def create_agent_graph():
    """Constroi a maquina de estados cognitivos."""
    workflow = StateGraph(MissionState)

    # 1. Definir os nós (nossos agentes especialistas)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("checklist", checklist_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("critic", critic_node)

    # 2. Definir o fluxo (Edges)
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "triage")
    workflow.add_edge("triage", "checklist")

    # 3. Ramificacao Condicional (Se faltar campo, para. Se tiver, minutador).
    workflow.add_conditional_edges(
        "checklist",
        route_after_checklist,
        {
            "draft": "draft",
            END: END
        }
    )

    # 4. Do minutador vai para o critico
    workflow.add_edge("draft", "critic")

    # 5. Loop de Auto-Correcao
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "draft": "draft",
            END: END
        }
    )

    return workflow.compile()

# Instancia global compilada
agent_app = create_agent_graph()
