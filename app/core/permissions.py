"""Fonte unica da verdade sobre acoes permitidas e proibidas do Agente SEI.

Regra de ouro (docs/02-regras-de-seguranca.md):
    O agente prepara, organiza e sugere. Ele NAO assina, NAO tramita,
    NAO envia, NAO conclui, NAO da ciencia e NAO usa senha do SEI.

Politica de seguranca: NEGACAO POR PADRAO.
Apenas o que estiver explicitamente em ALLOWED_ACTIONS pode ser executado.
Tudo o que estiver em FORBIDDEN_ACTIONS e bloqueado de forma dura e auditado.
Qualquer acao desconhecida e tratada como negada.
"""

from __future__ import annotations

from enum import Enum


class Action(str, Enum):
    """Catalogo canonico de acoes que o agente pode tentar executar."""

    # --- Permitidas (leitura / preparacao / apoio) ---
    LER_PROCESSO = "LER_PROCESSO"
    LER_DOCUMENTO = "LER_DOCUMENTO"
    RESUMIR = "RESUMIR"
    CLASSIFICAR = "CLASSIFICAR"
    IDENTIFICAR_PRAZO = "IDENTIFICAR_PRAZO"
    IDENTIFICAR_EVENTO = "IDENTIFICAR_EVENTO"
    CRIAR_EVENTO_AGENDA = "CRIAR_EVENTO_AGENDA"
    ADICIONAR_CONVIDADOS_AGENDA = "ADICIONAR_CONVIDADOS_AGENDA"
    ENVIAR_CONVITE_AGENDA = "ENVIAR_CONVITE_AGENDA"
    ENVIAR_ALERTA = "ENVIAR_ALERTA"
    GERAR_MINUTA = "GERAR_MINUTA"
    SALVAR_MINUTA = "SALVAR_MINUTA"
    REGISTRAR_LOG = "REGISTRAR_LOG"

    # --- Proibidas (atos oficiais do SEI) ---
    ASSINAR_DOCUMENTO = "ASSINAR_DOCUMENTO"
    ENVIAR_PROCESSO = "ENVIAR_PROCESSO"
    TRAMITAR_PROCESSO = "TRAMITAR_PROCESSO"
    CONCLUIR_PROCESSO = "CONCLUIR_PROCESSO"
    CANCELAR_DOCUMENTO = "CANCELAR_DOCUMENTO"
    EXCLUIR_DOCUMENTO = "EXCLUIR_DOCUMENTO"
    DAR_CIENCIA_AUTOMATICA = "DAR_CIENCIA_AUTOMATICA"
    CONCEDER_CREDENCIAL = "CONCEDER_CREDENCIAL"
    LIBERAR_ACESSO_EXTERNO = "LIBERAR_ACESSO_EXTERNO"
    ALTERAR_SIGILO_AUTOMATICAMENTE = "ALTERAR_SIGILO_AUTOMATICAMENTE"


# Acoes explicitamente permitidas.
ALLOWED_ACTIONS: frozenset[Action] = frozenset(
    {
        Action.LER_PROCESSO,
        Action.LER_DOCUMENTO,
        Action.RESUMIR,
        Action.CLASSIFICAR,
        Action.IDENTIFICAR_PRAZO,
        Action.IDENTIFICAR_EVENTO,
        Action.CRIAR_EVENTO_AGENDA,
        Action.ADICIONAR_CONVIDADOS_AGENDA,
        Action.ENVIAR_CONVITE_AGENDA,
        Action.ENVIAR_ALERTA,
        Action.GERAR_MINUTA,
        Action.SALVAR_MINUTA,
        Action.REGISTRAR_LOG,
    }
)

# Acoes proibidas de forma dura. NUNCA podem ser executadas pelo agente,
# independentemente de qualquer flag de configuracao.
FORBIDDEN_ACTIONS: frozenset[Action] = frozenset(
    {
        Action.ASSINAR_DOCUMENTO,
        Action.ENVIAR_PROCESSO,
        Action.TRAMITAR_PROCESSO,
        Action.CONCLUIR_PROCESSO,
        Action.CANCELAR_DOCUMENTO,
        Action.EXCLUIR_DOCUMENTO,
        Action.DAR_CIENCIA_AUTOMATICA,
        Action.CONCEDER_CREDENCIAL,
        Action.LIBERAR_ACESSO_EXTERNO,
        Action.ALTERAR_SIGILO_AUTOMATICAMENTE,
    }
)

# Acoes permitidas, porem SENSIVEIS: tem efeito externo/colateral e exigem
# aprovacao humana explicita antes da execucao (docs/02, item "guarda obrigatorio").
SENSITIVE_ACTIONS: frozenset[Action] = frozenset(
    {
        Action.CRIAR_EVENTO_AGENDA,
        Action.ADICIONAR_CONVIDADOS_AGENDA,
        Action.ENVIAR_CONVITE_AGENDA,
        Action.ENVIAR_ALERTA,
        Action.SALVAR_MINUTA,
    }
)


def coerce_action(action: "Action | str") -> Action | None:
    """Converte string em Action; devolve None se o nome for desconhecido."""
    if isinstance(action, Action):
        return action
    try:
        return Action(str(action).strip().upper())
    except ValueError:
        return None


def is_forbidden(action: "Action | str") -> bool:
    """True se a acao for um ato oficial proibido (bloqueio duro)."""
    resolved = coerce_action(action)
    return resolved is not None and resolved in FORBIDDEN_ACTIONS


def is_allowed(action: "Action | str") -> bool:
    """True somente se a acao estiver na lista positiva.

    Negacao por padrao: nome desconhecido ou fora da lista => False.
    """
    resolved = coerce_action(action)
    return resolved is not None and resolved in ALLOWED_ACTIONS


def is_sensitive(action: "Action | str") -> bool:
    """True se a acao for permitida porem exigir aprovacao humana."""
    resolved = coerce_action(action)
    return resolved is not None and resolved in SENSITIVE_ACTIONS

