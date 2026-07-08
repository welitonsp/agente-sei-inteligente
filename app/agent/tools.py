"""Registro de ferramentas permitidas do Agente 19."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentToolSpec:
    nome: str
    descricao: str
    permissao: str
    read_only: bool
    revisao_humana_obrigatoria: bool
    risk_level: str = "low"
    requires_human_approval: bool = False
    writes_external_system: bool = False
    writes_sei: bool = False
    allowed_actions: tuple[str, ...] = field(default_factory=tuple)

    def to_contract(self) -> dict[str, Any]:
        return {
            "nome": self.nome,
            "descricao": self.descricao,
            "permissao": self.permissao,
            "read_only": self.read_only,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "risk_level": self.risk_level,
            "requires_human_approval": self.requires_human_approval,
            "writes_external_system": self.writes_external_system,
            "writes_sei": self.writes_sei,
            "allowed_actions": list(self.allowed_actions),
        }


SAFE_AGENT_TOOLS: dict[str, AgentToolSpec] = {
    "mission_control": AgentToolSpec(
        nome="mission_control",
        descricao="Orquestra analise, triagem, minuta externa, riscos e pendencias.",
        permissao="analise_supervisionada",
        read_only=True,
        revisao_humana_obrigatoria=True,
        risk_level="low",
        requires_human_approval=False,
        writes_external_system=False,
        writes_sei=False,
        allowed_actions=("RESUMIR", "CLASSIFICAR", "IDENTIFICAR_PRAZO", "GERAR_MINUTA"),
    ),
    "calendar_agent": AgentToolSpec(
        nome="calendar_agent",
        descricao="Prepara evento Google Agenda; exige aprovacao antes de gravar.",
        permissao="efeito_externo_com_aprovacao",
        read_only=False,
        revisao_humana_obrigatoria=True,
        risk_level="medium",
        requires_human_approval=True,
        writes_external_system=True,
        writes_sei=False,
        allowed_actions=("CRIAR_EVENTO_AGENDA",),
    ),
    "notification_agent": AgentToolSpec(
        nome="notification_agent",
        descricao="Prepara alerta Telegram/e-mail; exige aprovacao antes de enviar.",
        permissao="efeito_externo_com_aprovacao",
        read_only=False,
        revisao_humana_obrigatoria=True,
        risk_level="medium",
        requires_human_approval=True,
        writes_external_system=True,
        writes_sei=False,
        allowed_actions=("ENVIAR_ALERTA",),
    ),
}


def get_agent_tool(name: str) -> AgentToolSpec:
    tool = SAFE_AGENT_TOOLS.get(name)
    if tool is None:
        raise PermissionError(f"Ferramenta nao registrada para o Agente 19: {name}")
    return tool


def list_agent_tools() -> list[dict[str, Any]]:
    return [tool.to_contract() for tool in SAFE_AGENT_TOOLS.values()]
