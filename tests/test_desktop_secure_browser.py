"""Contratos de seguranca do Agente 19 Desktop."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.desktop import secure_browser


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "app" / "desktop"


def test_desktop_abre_apenas_url_oficial_do_sei():
    opened: list[str] = []

    def fake_open(url: str) -> bool:
        opened.append(url)
        return True

    assert secure_browser.open_official_sei(fake_open) is True
    assert opened == ["https://sei.go.gov.br/sei/"]


def test_backend_do_desktop_e_somente_127_0_0_1():
    assert (
        secure_browser.validate_backend_origin("http://127.0.0.1:8000")
        == "http://127.0.0.1:8000"
    )

    for origin in [
        "https://sei.go.gov.br/sei/",
        "http://localhost:8000",
        "http://192.168.0.10:8000",
        "http://user:pass@127.0.0.1:8000",
    ]:
        with pytest.raises(ValueError):
            secure_browser.validate_backend_origin(origin)


def test_desktop_permite_apenas_endpoints_locais_previstos():
    assert secure_browser.ALLOWED_ENDPOINTS == {
        "/api/import-text",
        "/api/import-pdf",
        "/api/generate-draft",
        "/api/triage-local",
    }


def test_campos_do_desktop_nao_incluem_login_ou_senha_sei():
    field_names = {field.name.lower() for field in secure_browser.AGENT_INPUT_FIELDS}
    field_labels = {field.label.lower() for field in secure_browser.AGENT_INPUT_FIELDS}
    forbidden = {
        "senha",
        "password",
        "usuario_sei",
        "login_sei",
        "cookie",
        "session",
        "token",
        "credencial",
    }

    for fragment in forbidden:
        assert all(fragment not in name for name in field_names)
        assert all(fragment not in label for label in field_labels)


def test_payload_com_credencial_e_bloqueado():
    valid_payload = {
        "titulo": "Demanda",
        "texto": "Prazo ate 2026-07-01.",
        "processo_sei": "2026.0001",
        "usuario_local": "operador.local",
    }
    secure_browser.ensure_no_credential_payload(valid_payload)

    for payload in [
        {"senha": "abc"},
        {"password": "abc"},
        {"cookie": "abc"},
        {"token": "abc"},
        {"texto": "senha: abc"},
        {"texto": "token=abc"},
    ]:
        with pytest.raises(secure_browser.CredentialPolicyViolation):
            secure_browser.ensure_no_credential_payload(payload)


def test_codigo_desktop_nao_tem_campo_senha_nem_persistencia_credencial():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(DESKTOP.glob("*.py"))
    )

    forbidden_fragments = [
        'show="*"',
        "show='*'",
        'type="password"',
        "type='password'",
        "keyring",
        "browser_cookie3",
        "http.cookiejar",
        "document.cookie",
        "localStorage",
        "sessionStorage",
        "Set-Cookie",
        "Authorization",
        ".click(",
        "submit()",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_formatacao_resultado_traz_resumo_tipo_providencia_e_copia_manual():
    payload = {
        "status": "precisa_revisao",
        "resultado": {
            "resumo_executivo": "Texto recebido para analise local.",
            "evento": {"ha_evento": True, "data": "2026-07-01"},
            "prazo": {"ha_prazo": False},
        },
        "confianca": 0.4,
        "revisao_humana_obrigatoria": True,
        "acoes_sugeridas": ["REVISAR_EVENTO"],
        "campos_pendentes": ["local"],
    }

    formatted = secure_browser.format_analysis_result(payload)

    assert "Resumo:" in formatted
    assert "Tipo provavel: Demanda com possivel evento" in formatted
    assert "Providencia sugerida:" in formatted
    assert "atos oficiais no SEI devem ser praticados manualmente" in formatted


def test_formatacao_minuta_reforca_revisao_e_sem_assinatura():
    payload = {
        "resultado": {
            "tipo_minuta": "despacho",
            "texto": "DESPACHO\n\nTexto preliminar.",
            "providencia_sugerida": "encaminhar para providencias",
            "alertas": ["Revisao humana obrigatoria."],
        },
        "confianca": 0.55,
        "revisao_humana_obrigatoria": True,
        "campos_pendentes": ["unidade_destino"],
    }

    formatted = secure_browser.format_draft_result(payload)

    assert "Minuta local preliminar" in formatted
    assert "DESPACHO" in formatted
    assert "nao assina nem tramita" in formatted


def test_formatacao_triagem_reforca_indefinido_sem_regra():
    payload = {
        "resultado": {
            "interesse_19crpm": "indefinido",
            "unidade_sugerida": "",
            "tipo_minuta_sugerido": "",
            "providencia_sugerida": "Preencher knowledge base.",
            "regra_aplicada": "",
            "justificativa": "Knowledge base sem regras.",
        },
        "confianca": 0.0,
        "campos_pendentes": ["knowledge_base_regras"],
    }

    formatted = secure_browser.format_triage_result(payload)

    assert "Triagem local" in formatted
    assert "Unidade sugerida: indefinida" in formatted
    assert "nao direcione automaticamente" in formatted
