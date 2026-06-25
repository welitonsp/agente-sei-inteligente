"""Testes unitarios para o wrapper ReadOnlyPage."""

import pytest
from app.sei.read_only_page import ReadOnlyPage, ReadOnlyPageSnapshot

class FakeElement:
    """Elemento simulado com leitura de texto."""

    def __init__(self, texto: str) -> None:
        self._texto = texto

    def inner_text(self) -> str:
        return self._texto


class FakePage:
    """Mock simples simulando uma pagina Playwright."""

    @property
    def url(self) -> str:
        return "https://sei.go.gov.br/sei/controlador.php?acao=procedimento_trabalhar"

    def title(self) -> str:
        return "SEI - Controle de Processos"

    def text_content(self, selector: str) -> str:
        if selector == "body":
            return "Processo 202600000123456 aberto."
        return ""

    def query_selector_all(self, selector: str):
        if selector == "a":
            return [
                FakeElement("Despacho 123 (0001)"),
                FakeElement("Ofício 456 (0002)"),
                FakeElement("   "),  # vazio: deve ser ignorado
            ]
        return []


def test_read_only_page_permite_leitura_esperada():
    """Garante que a classe envelopa a pagina e extrai os dados sem acoes destrutivas."""
    fake_page = FakePage()
    ro_page = ReadOnlyPage(fake_page)

    assert ro_page.current_url() == "https://sei.go.gov.br/sei/controlador.php?acao=procedimento_trabalhar"
    assert ro_page.title() == "SEI - Controle de Processos"
    assert "202600000123456" in ro_page.visible_text()

    # Confirma o processo
    assert ro_page.confirm_process_number("202600000123456") is True
    assert ro_page.confirm_process_number("202600000999999") is False

    # Extrai o snapshot
    snap = ro_page.snapshot()
    assert isinstance(snap, ReadOnlyPageSnapshot)
    assert snap.url == "https://sei.go.gov.br/sei/controlador.php?acao=procedimento_trabalhar"
    assert snap.title == "SEI - Controle de Processos"


def test_read_only_page_nao_expoe_page_crua():
    """Garante que a instancia original do Playwright page nao esta publica."""
    fake_page = FakePage()
    ro_page = ReadOnlyPage(fake_page)

    assert not hasattr(ro_page, "page")
    assert not hasattr(ro_page, "get_page")


def test_read_only_page_bloqueia_metodos_escrita():
    """Garante que o wrapper nao oferece os metodos destrutivos do Playwright."""
    fake_page = FakePage()
    ro_page = ReadOnlyPage(fake_page)

    forbidden_methods = [
        "click",
        "fill",
        "goto",
        "press",
        "type",
        "evaluate",
        "set_input_files",
        "select_option",
        "dispatch_event"
    ]

    for method in forbidden_methods:
        assert not hasattr(ro_page, method), f"ReadOnlyPage nao deve possuir o metodo {method}"


def test_read_only_page_le_arvore_de_documentos():
    """A leitura da árvore devolve apenas títulos não vazios."""
    ro_page = ReadOnlyPage(FakePage())
    titulos = ro_page.document_tree()
    assert titulos == ("Despacho 123 (0001)", "Ofício 456 (0002)")


class FakeFrame:
    def __init__(self, name: str, url: str, links: list[str]) -> None:
        self.name = name
        self.url = url
        self._links = links

    def query_selector_all(self, selector: str):
        return [FakeElement(t) for t in self._links] if selector == "a" else []


def test_frames_overview_relata_frames_read_only():
    class PaginaComFrames(FakePage):
        @property
        def frames(self):
            return [
                FakeFrame("", "https://sei/topo", ["Menu"]),
                FakeFrame("ifrArvore", "https://sei/arvore", ["Despacho 1", "Ofício 2"]),
            ]

    overview = ReadOnlyPage(PaginaComFrames()).frames_overview()
    nomes = [f["name"] for f in overview]
    assert "ifrArvore" in nomes
    arvore = next(f for f in overview if f["name"] == "ifrArvore")
    assert arvore["num_links"] == 2
    assert "Despacho 1" in arvore["amostra"]


def test_frames_overview_vazio_sem_frames():
    assert ReadOnlyPage(FakePage()).frames_overview() == ()


def test_document_tree_tolerante_a_pagina_sem_query():
    """Sem query_selector_all a leitura da árvore retorna vazio, sem falhar."""

    class PaginaSemQuery:
        url = "x"

        def title(self) -> str:
            return "t"

        def text_content(self, selector: str) -> str:
            return ""

    ro_page = ReadOnlyPage(PaginaSemQuery())
    assert ro_page.document_tree() == ()
