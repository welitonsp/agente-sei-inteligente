import pytest
from app.sei.sei_action_guard import validate_action, ActionBlockedError

def test_validate_action_blocks_prohibited_actions():
    prohibited = [
        "assinar_documento", "tramitar_processo", "enviar_processo", 
        "concluir_processo", "capturar_senha", "excluir_documento",
        "cancelar_documento", "dar_ciencia", "capturar_cookie",
        "capturar_sessao", "capturar_token"
    ]
    for action in prohibited:
        with pytest.raises(ActionBlockedError):
            validate_action(action)

def test_validate_action_allows_valid_actions():
    assert validate_action("ler_documento") is True
    assert validate_action("gerar_minuta_em_memoria") is True
