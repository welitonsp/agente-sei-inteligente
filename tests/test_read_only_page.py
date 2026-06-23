"""Testes unitarios para o wrapper ReadOnlyPage."""

import pytest
from app.sei.read_only_page import ReadOnlyPage, ReadOnlyPageSnapshot

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
