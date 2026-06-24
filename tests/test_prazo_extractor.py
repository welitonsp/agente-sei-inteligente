"""Testes do extrator local de prazos."""

from __future__ import annotations

from datetime import date

from app.intelligence.prazo_extractor import extract_prazos


def test_prazo_relativo_em_dias():
    prazos = extract_prazos("Responder no prazo de 5 dias.")
    assert len(prazos) == 1
    p = prazos[0]
    assert p.tipo == "relativo"
    assert p.quantidade == 5
    assert p.unidade == "dias"
    assert p.dias_uteis is False


def test_prazo_por_extenso_e_dias_uteis():
    prazos = extract_prazos("Cumprir no prazo de 10 (dez) dias úteis.")
    assert len(prazos) == 1
    assert prazos[0].quantidade == 10
    assert prazos[0].dias_uteis is True


def test_prazo_em_horas():
    prazos = extract_prazos("Manifestar-se em 48 horas.")
    assert prazos[0].unidade == "horas"
    assert prazos[0].quantidade == 48


def test_prazo_relativo_calcula_data_limite():
    prazos = extract_prazos("Prazo de 5 dias.", reference_date=date(2026, 6, 24))
    assert prazos[0].data_limite == date(2026, 6, 29)


def test_prazo_dias_uteis_pula_fim_de_semana():
    # 2026-06-24 é quarta; 3 dias úteis -> qui, sex, seg (29/06).
    prazos = extract_prazos("No prazo de 3 dias úteis.", reference_date=date(2026, 6, 24))
    assert prazos[0].data_limite == date(2026, 6, 29)


def test_prazo_absoluto_numerico():
    prazos = extract_prazos("Apresentar defesa até 30/06/2026.")
    assert prazos[0].tipo == "absoluto"
    assert prazos[0].data_limite == date(2026, 6, 30)


def test_prazo_absoluto_por_extenso():
    prazos = extract_prazos("Comparecer até 30 de junho de 2026.")
    assert prazos[0].data_limite == date(2026, 6, 30)


def test_sem_prazo_retorna_vazio():
    assert extract_prazos("Documento meramente informativo.") == []


def test_data_invalida_e_ignorada():
    assert extract_prazos("até 31/02/2026") == []
