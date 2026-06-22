"""Contratos de seguranca da extensao read-only do SEI."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "browser_extension"


def test_manifest_restringe_hosts_e_nao_pede_cookies():
    manifest = json.loads((EXT / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["manifest_version"] == 3
    assert "cookies" not in manifest.get("permissions", [])
    assert "webRequest" not in manifest.get("permissions", [])
    assert manifest["host_permissions"] == [
        "https://sei.go.gov.br/sei/*",
        "http://127.0.0.1:8000/*",
    ]


def test_content_script_nao_clica_no_sei():
    content = (EXT / "content.js").read_text(encoding="utf-8")

    forbidden_fragments = [
        ".click(",
        "submit()",
        "dispatchEvent(",
        "chrome.cookies",
        "document.cookie",
        "localStorage.setItem",
        "sessionStorage.setItem",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in content


def test_content_script_bloqueia_termos_de_ato_oficial():
    content = (EXT / "content.js").read_text(encoding="utf-8").lower()

    for term in [
        "assinar",
        "enviar processo",
        "tramitar",
        "concluir",
        "dar ciência",
        "excluir",
        "cancelar",
        "alterar sigilo",
    ]:
        assert term in content


def test_background_usa_backend_local():
    background = (EXT / "background.js").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8000/api/import-text" in background
    assert "https://" not in background.replace("http://127.0.0.1:8000/api/import-text", "")
