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


def test_content_script_tem_ui_chat_profissional_readonly():
    content = (EXT / "content.js").read_text(encoding="utf-8")
    css = (EXT / "content.css").read_text(encoding="utf-8")

    assert "agente-sei-chat" in content
    assert "agente-sei-messages" in content
    assert "Pergunte sobre o processo aberto no SEI" in content
    assert "data-intent=\"resumo\"" in content
    assert "data-intent=\"prazo\"" in content
    assert "data-intent=\"providencia\"" in content
    assert "data-intent=\"minuta\"" in content
    assert "Login, senha, cookie e atos oficiais ficam fora" in content
    assert "Somente leitura" in content
    assert "Backend local" in content
    assert "Revisao humana" in content
    assert ".agente-sei-message" in css
    assert ".agente-sei-composer" in css
    assert ".agente-sei-statusbar" in css


def test_content_script_minuta_e_rascunho_externo_sem_escrita_no_sei():
    content = (EXT / "content.js").read_text(encoding="utf-8")

    assert "Rascunho externo de minuta" in content
    assert "copiar somente apos conferencia humana" in content
    assert "a insercao no SEI permanece manual" in content
    assert "formatDraftSuggestion" in content
    assert ".click(" not in content
    assert "dispatchEvent(" not in content


def test_content_script_continua_readonly_sem_storage_de_sessao():
    content = (EXT / "content.js").read_text(encoding="utf-8")

    forbidden_fragments = [
        "chrome.cookies",
        "document.cookie",
        "localStorage",
        "sessionStorage",
        "Authorization",
        "Set-Cookie",
        "password",
        "senha_sei",
        "login_sei",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in content


def test_background_usa_backend_local():
    background = (EXT / "background.js").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8000/api/import-text" in background
    assert "https://" not in background.replace("http://127.0.0.1:8000/api/import-text", "")


def test_preview_chat_local_usa_apenas_dados_ficticios():
    preview = (EXT / "preview_chat.html").read_text(encoding="utf-8")

    assert "content.css" in preview
    assert "content.js" in preview
    assert "Processo 202600000123456" in preview
    assert "Conteudo ficticio" in preview
    assert "homologacao" in preview
    assert "visual" in preview
    assert "window.chrome" in preview
    assert "sendMessage" in preview
    assert "minuta_sugerida" in preview
    assert "Despacho, a confirmar" in preview
    assert "https://sei.go.gov.br" not in preview
    assert "http://127.0.0.1" not in preview


def test_preview_chat_local_nao_tem_campo_senha_ou_cookie():
    preview = (EXT / "preview_chat.html").read_text(encoding="utf-8").lower()

    forbidden_fragments = [
        'type="password"',
        "document.cookie",
        "localstorage",
        "sessionstorage",
        "authorization",
        "set-cookie",
        "token",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in preview
