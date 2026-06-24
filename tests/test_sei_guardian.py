"""Testes da fachada SeiGuardian sobre o guard central."""

from __future__ import annotations

import pytest

from app.sei.sei_guardian import SeiGuardian
from app.sei.sei_action_guard import GuardDecision


def test_guardian_permite_acao_de_leitura():
    g = SeiGuardian()
    res = g.check("LER_PROCESSO")
    assert res.permitido is True
    assert res.decisao == GuardDecision.PERMITIDO


def test_guardian_bloqueia_ato_oficial():
    g = SeiGuardian()
    res = g.check("ASSINAR_DOCUMENTO")
    assert res.permitido is False
    assert res.decisao == GuardDecision.BLOQUEADO


def test_guardian_is_allowed_atalho():
    g = SeiGuardian()
    assert g.is_allowed("RESUMIR") is True
    assert g.is_allowed("TRAMITAR_PROCESSO") is False


def test_guardian_require_levanta_em_acao_proibida():
    g = SeiGuardian()
    with pytest.raises(PermissionError):
        g.require("EXCLUIR_DOCUMENTO")
