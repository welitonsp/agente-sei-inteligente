"""Testes da fonte da verdade de permissoes (negacao por padrao)."""

from app.core import permissions
from app.core.permissions import (
    ALLOWED_ACTIONS,
    FORBIDDEN_ACTIONS,
    Action,
)


def test_listas_permitida_e_proibida_nao_se_cruzam():
    assert ALLOWED_ACTIONS.isdisjoint(FORBIDDEN_ACTIONS)


def test_toda_acao_proibida_e_reconhecida():
    for action in FORBIDDEN_ACTIONS:
        assert permissions.is_forbidden(action) is True
        assert permissions.is_allowed(action) is False


def test_toda_acao_permitida_e_reconhecida():
    for action in ALLOWED_ACTIONS:
        assert permissions.is_allowed(action) is True
        assert permissions.is_forbidden(action) is False


def test_acao_desconhecida_e_negada_por_padrao():
    assert permissions.is_allowed("FAZER_QUALQUER_COISA") is False
    assert permissions.is_forbidden("FAZER_QUALQUER_COISA") is False
    assert permissions.coerce_action("INEXISTENTE") is None


def test_atos_oficiais_classicos_sao_proibidos():
    for nome in [
        "ASSINAR_DOCUMENTO",
        "ENVIAR_PROCESSO",
        "TRAMITAR_PROCESSO",
        "CONCLUIR_PROCESSO",
        "EXCLUIR_DOCUMENTO",
        "DAR_CIENCIA_AUTOMATICA",
    ]:
        assert permissions.is_forbidden(nome) is True


def test_acoes_sensiveis_estao_dentro_das_permitidas():
    assert permissions.SENSITIVE_ACTIONS <= ALLOWED_ACTIONS
    assert permissions.is_sensitive(Action.ENVIAR_ALERTA) is True
    assert permissions.is_sensitive(Action.RESUMIR) is False
