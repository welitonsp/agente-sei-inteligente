"""Guarda central de acoes do SEI (skill `guardiao-seguranca-sei`).

Toda rotina que pretenda executar uma acao externa deve passar por aqui ANTES
de qualquer clique, chamada de API ou automacao web.

Contrato (docs/24-contratos-das-skills.md):
    Entrada: acao_solicitada, origem, usuario_local, processo_sei, justificativa
    Saida:   permitido, motivo, acao, deve_registrar_log

Decisao do guard:
    1. Acao proibida (ato oficial)         -> BLOQUEADO    (bloqueio duro)
    2. Acao fora da lista positiva         -> BLOQUEADO    (negacao por padrao)
    3. Acao sensivel sem aprovacao humana  -> PRECISA_REVISAO
    4. Demais acoes permitidas             -> PERMITIDO

O guard NUNCA confia em flag de ambiente para liberar um ato oficial: acoes
proibidas permanecem bloqueadas mesmo que ALLOW_OFFICIAL_SEI_ACTIONS seja
indevidamente ligado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core import permissions
from app.core.permissions import Action


class GuardDecision(str, Enum):
    PERMITIDO = "permitido"
    BLOQUEADO = "bloqueado"
    PRECISA_REVISAO = "precisa_revisao"


@dataclass(frozen=True)
class GuardRequest:
    """Intencao de acao submetida ao guard."""

    acao_solicitada: str
    origem: str = ""
    usuario_local: str = ""
    estacao: str = ""
    processo_sei: str = ""
    justificativa: str = ""
    aprovado_por_humano: bool = False


@dataclass(frozen=True)
class GuardResult:
    """Resposta do guard, sempre auditavel."""

    permitido: bool
    decisao: GuardDecision
    motivo: str
    acao: str
    deve_registrar_log: bool = True
    revisao_humana_obrigatoria: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        """Serializa no formato do contrato `guardiao-seguranca-sei`."""
        return {
            "permitido": self.permitido,
            "motivo": self.motivo,
            "acao": self.acao,
            "deve_registrar_log": self.deve_registrar_log,
        }


def evaluate(request: GuardRequest) -> GuardResult:
    """Avalia uma intencao de acao e devolve a decisao do guard.

    Esta funcao e PURA: nao executa a acao, nao toca em I/O e nao registra log
    por conta propria. O chamador e responsavel por persistir a auditoria
    (ver app/core/audit.py) e por so prosseguir quando `permitido` for True.
    """
    nome_acao = str(request.acao_solicitada).strip().upper()
    resolved = permissions.coerce_action(nome_acao)

    # 1) Acao desconhecida -> negacao por padrao.
    if resolved is None:
        return GuardResult(
            permitido=False,
            decisao=GuardDecision.BLOQUEADO,
            motivo=f"Acao desconhecida '{nome_acao}'. Negada por padrao.",
            acao=nome_acao,
            metadata={"regra": "default_deny_desconhecida"},
        )

    # 2) Ato oficial proibido -> bloqueio duro (ignora qualquer flag).
    if permissions.is_forbidden(resolved):
        return GuardResult(
            permitido=False,
            decisao=GuardDecision.BLOQUEADO,
            motivo=(
                "Ato oficial do SEI e proibido para o agente. "
                "Deve ser praticado manualmente pelo servidor."
            ),
            acao=resolved.value,
            revisao_humana_obrigatoria=True,
            metadata={"regra": "forbidden_hard_block"},
        )

    # 3) Fora da lista positiva -> negacao por padrao.
    if not permissions.is_allowed(resolved):
        return GuardResult(
            permitido=False,
            decisao=GuardDecision.BLOQUEADO,
            motivo=f"Acao '{resolved.value}' nao esta na lista positiva.",
            acao=resolved.value,
            metadata={"regra": "default_deny_fora_da_lista"},
        )

    # 4) Acao sensivel sem aprovacao humana -> precisa revisao.
    if permissions.is_sensitive(resolved) and not request.aprovado_por_humano:
        return GuardResult(
            permitido=False,
            decisao=GuardDecision.PRECISA_REVISAO,
            motivo=(
                f"Acao '{resolved.value}' tem efeito externo e exige "
                "aprovacao humana explicita."
            ),
            acao=resolved.value,
            revisao_humana_obrigatoria=True,
            metadata={"regra": "sensivel_requer_aprovacao"},
        )

    # 5) Permitida.
    return GuardResult(
        permitido=True,
        decisao=GuardDecision.PERMITIDO,
        motivo="Acao permitida pela lista positiva.",
        acao=resolved.value,
        metadata={"regra": "lista_positiva"},
    )


def assert_allowed(request: GuardRequest) -> GuardResult:
    """Versao defensiva: levanta excecao se a acao nao for permitida.

    Util para envolver chamadas a integracoes externas de modo que um caminho
    de codigo jamais execute um ato proibido por engano.
    """
    result = evaluate(request)
    if not result.permitido:
        raise PermissionError(
            f"[GUARD] {result.decisao.value.upper()}: {result.motivo}"
        )
    return result

