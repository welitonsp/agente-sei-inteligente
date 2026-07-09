"""Testes do retriever RAG dos manuais (local, deterministico, sem rede)."""

from __future__ import annotations

from pathlib import Path

from app.intelligence.manual_retriever import (
    Chunk,
    ManualRetriever,
    get_default_retriever,
    load_chunks,
    retrieve_context,
    tokenize,
)

_SAMPLE = """# Titulo do arquivo

## Niveis de acesso
O acesso pode ser publico, restrito ou sigiloso. Sigiloso exige hipotese legal.

## Fecho adequado
Use Respeitosamente para autoridade superior e Atenciosamente para igual.
"""


def _make_retriever(tmp_path: Path) -> ManualRetriever:
    (tmp_path / "amostra.md").write_text(_SAMPLE, encoding="utf-8")
    (tmp_path / "README.md").write_text("# ignore me\n## nao deve virar regra", encoding="utf-8")
    chunks = load_chunks((tmp_path,))
    return ManualRetriever(chunks)


# --- tokenizacao -------------------------------------------------------------


def test_tokenize_remove_acento_e_stopword():
    toks = tokenize("O nível de acesso é sigiloso")
    assert "nivel" in toks
    assert "sigiloso" in toks
    assert "de" not in toks  # stopword
    assert "o" not in toks  # token curto/stopword


# --- fatiamento --------------------------------------------------------------


def test_load_chunks_fatia_por_titulo_e_ignora_readme(tmp_path):
    retr = _make_retriever(tmp_path)
    assert retr.size == 2  # duas regras; README ignorado; H1 nao vira regra


# --- ranqueamento ------------------------------------------------------------


def test_retrieve_traz_regra_mais_relevante(tmp_path):
    retr = _make_retriever(tmp_path)
    res = retr.retrieve("qual o nivel de acesso sigiloso do processo", k=2)
    assert res
    assert res[0].chunk.title == "Niveis de acesso"
    assert res[0].score > 0


def test_retrieve_sem_termo_conhecido_retorna_vazio(tmp_path):
    retr = _make_retriever(tmp_path)
    assert retr.retrieve("xyzzy plugh", k=3) == []


def test_retrieve_query_vazia_retorna_vazio(tmp_path):
    retr = _make_retriever(tmp_path)
    assert retr.retrieve("", k=3) == []


def test_retriever_deterministico(tmp_path):
    retr = _make_retriever(tmp_path)
    a = retr.retrieve("fecho respeitosamente autoridade", k=2)
    b = retr.retrieve("fecho respeitosamente autoridade", k=2)
    assert [r.chunk.title for r in a] == [r.chunk.title for r in b]


def test_retriever_vazio_nao_quebra():
    retr = ManualRetriever([])
    assert retr.retrieve("qualquer coisa", k=3) == []


# --- base curada real + contexto ---------------------------------------------


def test_base_curada_padrao_tem_regras():
    retr = get_default_retriever()
    assert retr.size >= 8  # regras do SEI + redacao de Goias


def test_retrieve_context_traz_fonte_para_minuta():
    ctx = retrieve_context("nivel de acesso sigiloso e hipotese legal", k=3)
    assert ctx
    assert "REGRAS DOS MANUAIS" in ctx
    assert "regras_operacionais.md" in ctx  # grounding com fonte


def test_retrieve_context_gibberish_vazio():
    assert retrieve_context("zzz qqq wpf", k=3) == ""


def test_chunk_dataclass_congelado():
    c = Chunk(source="x.md", title="t", text="corpo", tokens=frozenset({"corpo"}))
    assert c.title == "t"
