"""Registro de ferramentas permitidas do Agente 19."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentToolSpec:
    nome: str
    descricao: str
    permissao: str
    read_only: bool
    revisao_humana_obrigatoria: bool

    def to_contract(self) -> dict[str, object]:
        return {
            "nome": self.nome,
            "descricao": self.descricao,
            "permissao": self.permissao,
            "read_only": self.read_only,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
        }


SAFE_AGENT_TOOLS: dict[str, AgentToolSpec] = {
    "mission_control": AgentToolSpec(
        nome="mission_control",
        descricao="Orquestra analise, triagem, minuta externa, riscos e pendencias.",
        permissao="analise_supervisionada",
        read_only=True,
        revisao_humana_obrigatoria=True,
    )
}


def get_agent_tool(name: str) -> AgentToolSpec:
    tool = SAFE_AGENT_TOOLS.get(name)
    if tool is None:
        raise PermissionError(f"Ferramenta nao registrada para o Agente 19: {name}")
    return tool


def list_agent_tools() -> list[dict[str, object]]:
    return [tool.to_contract() for tool in SAFE_AGENT_TOOLS.values()]
