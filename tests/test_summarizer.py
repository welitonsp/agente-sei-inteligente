"""Testes do resumidor extractivo local."""

from __future__ import annotations

from app.intelligence.summarizer import summarize


def test_resumo_vazio():
    assert summarize("") == ""
    assert summarize("   ") == ""


def test_resumo_seleciona_frases_relevantes():
    texto = (
        "Bom dia a todos. "
        "Solicita-se a elaboração de ofício em resposta à requisição. "
        "O prazo para manifestação é de 5 dias. "
        "Atenciosamente."
    )
    resumo = summarize(texto, max_frases=2)
    # Deve priorizar as frases com sinais administrativos (ofício/prazo).
    assert "ofício" in resumo.lower() or "prazo" in resumo.lower()
    # Não é mais a string fixa antiga.
    assert resumo != "Resumo gerado por regras simples"


def test_resumo_sanitiza_pii():
    texto = "Intimação ao CPF 123.456.789-00 para responder no prazo de 5 dias."
    resumo = summarize(texto)
    assert "123.456.789-00" not in resumo
    assert "123.***.***-00" in resumo


def test_resumo_curto_passa_direto():
    texto = "Despacho para análise."
    assert "despacho" in summarize(texto).lower()
