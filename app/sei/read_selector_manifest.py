"""Manifesto de seletores de LEITURA do SEI (FASE 5C — Frente 2).

Valida um contrato estático de seletores usados apenas para LER um processo
aberto pela sessão logada do usuário (confirmar número, ler a árvore de
documentos e o conteúdo visível). Não executa navegador, não clica e não
escreve. Reaproveita os termos proibidos e os status do manifesto de escrita.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.sei.selector_manifest import ALLOWED_STATUSES, FORBIDDEN_SELECTOR_TERMS

# Seletores mínimos para o agente LER um processo (somente leitura).
# Homologado no SEI Goiás: o processo é montado em frames nomeados; a árvore de
# documentos vive em `ifrArvore` e o conteúdo em `ifrVisualizacao`.
REQUIRED_READ_SELECTOR_KEYS = (
    "tree_frame",       # nome do frame da árvore de documentos (confirma o nº e lista docs)
    "content_frame",    # nome do frame de visualização do conteúdo
)


@dataclass(frozen=True)
class ReadSelectorManifestReport:
    ok: bool
    version: str
    missing: tuple[str, ...]
    not_homologated: tuple[str, ...]
    forbidden: tuple[str, ...]

    @property
    def blockers(self) -> tuple[str, ...]:
        return self.missing + self.not_homologated + self.forbidden


def load_read_selector_manifest(path: str | Path) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Manifesto de leitura deve ser um objeto JSON.")
    return parsed


def evaluate_read_selector_manifest(manifest: dict[str, Any]) -> ReadSelectorManifestReport:
    version = str(manifest.get("version", ""))
    selectors = manifest.get("selectors", {})
    if not isinstance(selectors, dict):
        selectors = {}

    missing: list[str] = []
    not_homologated: list[str] = []
    forbidden: list[str] = []

    for key in REQUIRED_READ_SELECTOR_KEYS:
        selector = selectors.get(key)
        if not isinstance(selector, dict):
            missing.append(key)
            continue
        value = str(selector.get("value", "")).strip()
        status = str(selector.get("status", "")).strip().lower()
        if not value:
            missing.append(key)
        if status != "validated" or status not in ALLOWED_STATUSES:
            not_homologated.append(key)
        _collect_forbidden(key, value, forbidden)

    # Nenhum seletor de leitura pode apontar para ato oficial (escrita).
    for key, selector in selectors.items():
        value = str(selector.get("value", "")) if isinstance(selector, dict) else ""
        _collect_forbidden(str(key), value, forbidden)

    unique_forbidden = tuple(dict.fromkeys(forbidden))
    return ReadSelectorManifestReport(
        ok=not missing and not not_homologated and not unique_forbidden,
        version=version,
        missing=tuple(dict.fromkeys(missing)),
        not_homologated=tuple(dict.fromkeys(not_homologated)),
        forbidden=unique_forbidden,
    )


def _collect_forbidden(key: str, value: str, violations: list[str]) -> None:
    haystack = f"{key} {value}".lower()
    for term in FORBIDDEN_SELECTOR_TERMS:
        if term in haystack:
            violations.append(f"seletor de leitura proibido: {key}")
            return
