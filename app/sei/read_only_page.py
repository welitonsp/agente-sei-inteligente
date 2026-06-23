"""Wrapper read-only para pagina do SEI.

Esta classe nao expõe a pagina Playwright crua e nao oferece metodos de clique,
preenchimento, navegacao ou avaliacao arbitraria. Leitura e feita por metodos
pequenos e auditaveis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


PROCESS_NUMBER_PATTERN = re.compile(r"\b\d{4,}\.?\d{4,}[\d./-]*\b")


@dataclass(frozen=True)
class ReadOnlyPageSnapshot:
    """Retrato minimo da tela lida, sem HTML integral."""

    url: str
    title: str
    visible_text: str


class ReadOnlyPage:
    """Facade de leitura que impede acesso direto a metodos de escrita."""

    __slots__ = ("_page",)

    def __init__(self, page: Any) -> None:
        self._page = page

    def current_url(self) -> str:
        return str(getattr(self._page, "url", ""))

    def title(self) -> str:
        title_method = getattr(self._page, "title")
        return str(title_method())

    def visible_text(self) -> str:
        text_content = getattr(self._page, "text_content")
        return str(text_content("body") or "")

    def snapshot(self) -> ReadOnlyPageSnapshot:
        return ReadOnlyPageSnapshot(
            url=self.current_url(),
            title=self.title(),
            visible_text=self.visible_text(),
        )

    def confirm_process_number(self, expected_process: str) -> bool:
        expected = _digits(expected_process)
        if not expected:
            return False
        visible = _digits(self.visible_text())
        return expected in visible

    def visible_process_numbers(self) -> tuple[str, ...]:
        text = self.visible_text()
        return tuple(match.group(0) for match in PROCESS_NUMBER_PATTERN.finditer(text))


def _digits(value: str) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())
