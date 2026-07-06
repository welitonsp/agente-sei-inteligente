"""Fachada fina e estável sobre o guard central de ações do SEI.

`SeiGuardian` é um adaptador de conveniência: toda a lógica de decisão vive em
`app/sei/sei_action_guard.py` (função pura `evaluate`). Esta classe apenas
encaminha a intenção de ação, mantendo um ponto de entrada simples para
chamadores que só têm o nome da ação.
"""

from __future__ import annotations

from typing import Any
from app.sei.sei_action_guard import GuardRequest, GuardResult, assert_allowed, evaluate


class SeiGuardian:
    """Adaptador read-friendly sobre `sei_action_guard.evaluate`."""

    def check(self, action: str, **contexto: Any) -> GuardResult:
        """Avalia uma ação e devolve a decisão completa (sem executar nada)."""
        return evaluate(GuardRequest(acao_solicitada=action, **contexto))

    def is_allowed(self, action: str, **contexto: Any) -> bool:
        """Atalho booleano: True somente se a ação for permitida."""
        return self.check(action, **contexto).permitido

    def require(self, action: str, **contexto: Any) -> GuardResult:
        """Levanta PermissionError se a ação não for permitida."""
        return assert_allowed(GuardRequest(acao_solicitada=action, **contexto))
