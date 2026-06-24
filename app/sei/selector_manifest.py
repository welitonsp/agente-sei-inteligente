"""Manifesto de seletores para FASE 5B em homologacao.

Este modulo valida um contrato estatico de seletores. Ele nao executa navegador,
nao clica e nao preenche campos.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_SELECTOR_KEYS = (
    "process_number_area",
    "include_document_button",
    "document_type_search",
    "document_type_option",
    "document_description",
    "document_access_level",
    "editor_frame",
    "editor_body",
    "save_button",
)

FORBIDDEN_SELECTOR_TERMS = (
    "assinar",
    "tramitar",
    "enviar",
    "concluir",
    "ciencia",
    "ciência",
    "cancelar",
    "excluir",
    "liberar_acesso_externo",
)

ALLOWED_STATUSES = ("required", "optional", "pending", "validated")


@dataclass(frozen=True)
class SelectorManifestReport:
    """Resultado da validacao de seletores."""

    ok: bool
    version: str
    missing: tuple[str, ...]
    not_homologated: tuple[str, ...]
    forbidden: tuple[str, ...]

    @property
    def blockers(self) -> tuple[str, ...]:
        return self.missing + self.not_homologated + self.forbidden


def load_selector_manifest(path: str | Path) -> dict[str, Any]:
    """Carrega manifesto JSON de seletores."""
    raw = Path(path).read_text(encoding="utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Manifesto de seletores deve ser um objeto JSON.")
    return parsed


def evaluate_selector_manifest(manifest: dict[str, Any]) -> SelectorManifestReport:
    """Avalia se o manifesto esta pronto para homologacao controlada."""
    version = str(manifest.get("version", ""))
    selectors = manifest.get("selectors", {})
    if not isinstance(selectors, dict) or not selectors:
        selectors = {}

    missing: list[str] = []
    not_homologated: list[str] = []
    forbidden: list[str] = []

    if not selectors:
        missing.extend(REQUIRED_SELECTOR_KEYS)

    for key in REQUIRED_SELECTOR_KEYS:
        if key not in selectors and key not in missing:
            missing.append(key)
            continue
            
        selector = selectors.get(key)
        if not isinstance(selector, dict):
            if key not in missing:
                missing.append(key)
            continue
            
        value = str(selector.get("value", "")).strip()
        status = str(selector.get("status", "")).strip().lower()
        
        if not value:
            if key not in missing:
                missing.append(key)
        
        if status == "pending" or status not in ALLOWED_STATUSES or status != "validated":
            if key not in not_homologated:
                not_homologated.append(key)
                
        _collect_forbidden_terms(key, value, forbidden)

    for key, selector in selectors.items():
        value = ""
        if isinstance(selector, dict):
            value = str(selector.get("value", ""))
            status = str(selector.get("status", "")).strip().lower()
            if status == "pending" and key not in not_homologated:
                not_homologated.append(key)
        _collect_forbidden_terms(str(key), value, forbidden)

    unique_forbidden = tuple(dict.fromkeys(forbidden))
    return SelectorManifestReport(
        ok=not missing and not not_homologated and not unique_forbidden,
        version=version,
        missing=tuple(dict.fromkeys(missing)),
        not_homologated=tuple(dict.fromkeys(not_homologated)),
        forbidden=unique_forbidden,
    )


def _collect_forbidden_terms(key: str, value: str, violations: list[str]) -> None:
    haystack = f"{key} {value}".lower()
    for term in FORBIDDEN_SELECTOR_TERMS:
        if term in haystack:
            violations.append(f"seletor proibido: {key}")
            return
