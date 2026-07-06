"""Wrapper read-only para pagina do SEI.

Esta classe nao expõe a pagina Playwright crua e nao oferece metodos de clique,
preenchimento, navegacao ou avaliacao arbitraria. Leitura e feita por metodos
pequenos e auditaveis.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


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

    def document_tree(self) -> tuple[str, ...]:
        """Lê os títulos dos documentos da árvore do processo, somente leitura.

        Usa um acessor de leitura (`query_selector_all`) defensivamente: se a
        página não o expuser, devolve tupla vazia em vez de falhar. Nenhum
        clique, navegação ou escrita é realizado.
        """
        query = getattr(self._page, "query_selector_all", None)
        if not callable(query):
            return ()
        titulos: list[str] = []
        for elemento in query("a") or ():
            texto = _element_text(elemento)
            if texto:
                titulos.append(texto)
        return tuple(titulos)

    def _frame(self, name: str) -> Any:
        for frame in getattr(self._page, "frames", None) or ():
            if str(getattr(frame, "name", "") or "") == name:
                return frame
        return None

    def frame_links(self, name: str) -> tuple[str, ...]:
        """Lê os textos dos links de um frame nomeado (somente leitura)."""
        frame = self._frame(name)
        if frame is None:
            return ()
        query = getattr(frame, "query_selector_all", None)
        if not callable(query):
            return ()
        out: list[str] = []
        for elemento in query("a") or ():
            texto = _element_text(elemento)
            if texto:
                out.append(texto)
        return tuple(out)

    def frame_text(self, name: str) -> str:
        """Lê o texto visível do corpo de um frame nomeado (somente leitura)."""
        frame = self._frame(name)
        if frame is None:
            return ""
        for attr in ("inner_text", "text_content"):
            metodo = getattr(frame, attr, None)
            if callable(metodo):
                try:
                    valor = metodo("body")
                except Exception as exc:
                    logger.debug("Falha na extração '%s' no frame '%s'. Erro: %s", attr, name, exc)
                    continue
                if valor:
                    return str(valor).strip()
        return ""

    def frames_overview(self) -> tuple[dict[str, Any], ...]:
        """Diagnóstico read-only dos frames (o SEI monta o processo em iframes).

        Para cada frame, relata nome, URL, contagem de links e uma amostra dos
        textos — sem clicar, navegar ou escrever. Ajuda a homologar onde está a
        árvore de documentos e o conteúdo.
        """
        frames = getattr(self._page, "frames", None)
        if not frames:
            return ()
        overview: list[dict[str, Any]] = []
        for frame in frames:
            try:
                query = getattr(frame, "query_selector_all", None)
                anchors = list(query("a") or ()) if callable(query) else []
                amostra = []
                for elemento in anchors[:8]:
                    texto = _element_text(elemento)
                    if texto:
                        amostra.append(texto)
                overview.append(
                    {
                        "name": str(getattr(frame, "name", "") or ""),
                        "url": str(getattr(frame, "url", "") or ""),
                        "num_links": len(anchors),
                        "amostra": amostra,
                    }
                )
            except Exception as exc:
                logger.debug("Falha no frame '%s': %s", getattr(frame, "name", ""), exc)
                continue
        return tuple(overview)


def _digits(value: str) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())


def _element_text(elemento: Any) -> str:
    """Extrai texto de um elemento de forma read-only e tolerante."""
    for attr in ("inner_text", "text_content"):
        metodo = getattr(elemento, attr, None)
        if callable(metodo):
            try:
                texto = metodo()
            except Exception as exc:
                logger.debug("Falha ao extrair texto com '%s': %s", attr, exc)
                continue
            if texto:
                return str(texto).strip()
    return ""
