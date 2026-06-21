"""Testes obrigatorios de seguranca do guard do SEI (docs/16).

Estes testes sao o GATE: nenhum ato oficial pode passar.
"""

import pytest

from app.sei.sei_action_guard import (
    GuardDecision,
    GuardRequest,
    GuardResult,
    assert_allowed,
    evaluate,
)

ATOS_OFICIAIS = [
    "ASSINAR_DOCUMENTO",
    "ENVIAR_PROCESSO",
    "TRAMITAR_PROCESSO",
    "CONCLUIR_PROCESSO",
    "EXCLUIR_DOCUMENTO",
    "CANCELAR_DOCUMENTO",
    "DAR_CIENCIA_AUTOMATICA",
    "CONCEDER_CREDENCIAL",
    "LIBERAR_ACESSO_EXTERNO",
    "ALTERAR_SIGILO_AUTOMATICAMENTE",
]


@pytest.mark.parametrize("acao", ATOS_OFICIAIS)
def test_ato_oficial_e_sempre_bloqueado(acao):
    res = evaluate(GuardRequest(acao_solicitada=acao))
    assert res.permitido is False
    assert res.decisao is GuardDecision.BLOQUEADO
    assert res.deve_registrar_log is True


@pytest.mark.parametrize("acao", ATOS_OFICIAIS)
def test_ato_oficial_nao_passa_nem_com_aprovacao_humana(acao):
    # Aprovacao humana NAO libera ato oficial proibido.
    res = evaluate(GuardRequest(acao_solicitada=acao, aprovado_por_humano=True))
    assert res.permitido is False
    assert res.decisao is GuardDecision.BLOQUEADO


def test_leitura_e_permitida():
    res = evaluate(GuardRequest(acao_solicitada="LER_DOCUMENTO"))
    assert res.permitido is True
    assert res.decisao is GuardDecision.PERMITIDO


def test_resumir_e_classificar_sao_permitidos():
    for acao in ["RESUMIR", "CLASSIFICAR", "IDENTIFICAR_PRAZO"]:
        assert evaluate(GuardRequest(acao_solicitada=acao)).permitido is True


def test_acao_sensivel_sem_aprovacao_pede_revisao():
    res = evaluate(GuardRequest(acao_solicitada="ENVIAR_ALERTA"))
    assert res.permitido is False
    assert res.decisao is GuardDecision.PRECISA_REVISAO
    assert res.revisao_humana_obrigatoria is True


def test_acao_sensivel_com_aprovacao_e_liberada():
    res = evaluate(
        GuardRequest(acao_solicitada="ENVIAR_ALERTA", aprovado_por_humano=True)
    )
    assert res.permitido is True
    assert res.decisao is GuardDecision.PERMITIDO


def test_acao_desconhecida_e_negada():
    res = evaluate(GuardRequest(acao_solicitada="HACKEAR_SEI"))
    assert res.permitido is False
    assert res.decisao is GuardDecision.BLOQUEADO


def test_assert_allowed_levanta_em_acao_proibida():
    with pytest.raises(PermissionError):
        assert_allowed(GuardRequest(acao_solicitada="ASSINAR_DOCUMENTO"))


def test_contrato_de_saida_tem_campos_obrigatorios():
    res = evaluate(GuardRequest(acao_solicitada="ASSINAR_DOCUMENTO"))
    contrato = res.to_contract()
    assert set(contrato) == {"permitido", "motivo", "acao", "deve_registrar_log"}
    assert isinstance(res, GuardResult)
