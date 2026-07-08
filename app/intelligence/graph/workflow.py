"""Workflow deterministico de missao supervisionada.

Mantem a interface `agent_app.invoke(state)` usada pelo painel local, sem exigir
`langgraph` no ambiente de testes. A execucao delega ao Mission Control seguro,
que gera rascunho local, pacote de revisao humana e bloqueios de atos oficiais.
"""

from __future__ import annotations

from typing import Any

from app.intelligence.graph.state import MissionState
from app.intelligence.mission_control import MissionRequest, execute_mission


class DeterministicMissionApp:
    """Adaptador simples compativel com o contrato antigo do painel."""

    def invoke(self, state: MissionState) -> dict[str, Any]:
        result = execute_mission(
            MissionRequest(
                titulo=state.get("titulo", ""),
                texto=state.get("texto_original", ""),
                processo_sei=state.get("processo_sei", ""),
                usuario_local=state.get("usuario_local", ""),
                unidade_destino=state.get("unidade_destino", ""),
                tipo_minuta=state.get("tipo_minuta", ""),
                origem="graph_workflow_deterministico",
            )
        ).to_contract()
        resultado = result.get("resultado", {})
        minuta = resultado.get("minuta", {})
        triagem = resultado.get("triagem", {})
        return {
            **state,
            "status": result.get("status", "precisa_revisao"),
            "campos_pendentes": result.get("campos_pendentes", []),
            "confianca": result.get("confianca", 0.0),
            "revisao_humana_obrigatoria": result.get(
                "revisao_humana_obrigatoria", True
            ),
            "unidade_destino": triagem.get(
                "unidade_sugerida", state.get("unidade_destino", "")
            ),
            "tipo_minuta": minuta.get("tipo_minuta", state.get("tipo_minuta", "")),
            "minuta_texto": minuta.get("texto", ""),
            "alertas": resultado.get("riscos", []),
            "plano_operacional": resultado.get("plano_operacional", []),
            "etapa_recomendada": resultado.get("etapa_recomendada", ""),
        }


def create_agent_graph() -> DeterministicMissionApp:
    """Retorna o workflow compilado no formato esperado pelo painel."""
    return DeterministicMissionApp()


agent_app = create_agent_graph()
