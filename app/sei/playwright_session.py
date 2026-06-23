"""Sessao Playwright efemera para leitura supervisionada do SEI.

Este e o unico arquivo autorizado a usar navegacao Playwright direta. A sessao
nao usa perfil persistente e abre apenas a URL oficial do SEI para login manual.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from app.core.config import Settings, get_settings
from app.sei.read_only_page import ReadOnlyPage


@contextmanager
def open_ephemeral_readonly_session(
    settings: Settings | None = None,
) -> Iterator[ReadOnlyPage]:
    """Abre navegador efemero e devolve somente um wrapper read-only.

    Requer `ENABLE_SEI_BROWSER_AUTOMATION=true`; por padrao fica desligado.
    """
    cfg = settings or get_settings()
    if not cfg.enable_sei_browser_automation:
        raise PermissionError("Automacao de navegador SEI esta desabilitada.")

    from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(cfg.sei_base_url)
            yield ReadOnlyPage(page)
        finally:
            context.close()
            browser.close()
