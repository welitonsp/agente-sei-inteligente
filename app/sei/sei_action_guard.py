class ActionBlockedError(Exception):
    pass

PROHIBITED_ACTIONS = {
    "assinar_documento",
    "tramitar_processo",
    "enviar_processo",
    "concluir_processo",
    "excluir_documento",
    "cancelar_documento",
    "dar_ciencia",
    "capturar_senha",
    "capturar_cookie",
    "capturar_sessao",
    "capturar_token"
}

def validate_action(action_name: str) -> bool:
    """
    Valida se uma ação no SEI é permitida.
    Levanta ActionBlockedError se for proibida.
    """
    if action_name in PROHIBITED_ACTIONS:
        raise ActionBlockedError(f"Ação de automação bloqueada por política de segurança institucional: {action_name}")
    return True
