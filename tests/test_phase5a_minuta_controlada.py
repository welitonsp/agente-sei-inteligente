"""Testes da FASE 5A e do PATCH 4 de hardening."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.safety import evaluate_safety
from app.sei.minuta_token import generate_minuta_token, text_hash
from app.sei.minuta_writer import MinutaWriter


def test_safety_bloqueia_secret_padrao_em_producao():
    report = evaluate_safety(
        Settings(
            app_env="prod",
            minuta_token_secret="dev-insecure-trocar-em-producao",
        )
    )

    assert not report.ok
    assert "MINUTA_TOKEN_SECRET padrao em producao." in report.violations
    assert "MINUTA_TOKEN_SECRET curto em producao." in report.violations


def test_safety_bloqueia_minuta_creation_em_prod_sem_fase_5b():
    report = evaluate_safety(
        Settings(
            app_env="prod",
            minuta_token_secret="x" * 32,
            enable_minuta_creation=True,
        )
    )

    assert not report.ok
    assert (
        "ENABLE_MINUTA_CREATION ligado em producao sem FASE 5B homologada."
        in report.violations
    )


def test_safety_local_permite_defaults_de_desenvolvimento():
    report = evaluate_safety(Settings(app_env="local"))

    assert report.ok
    assert report.violations == ()


def test_minuta_writer_simula_e_audita_apenas_hash(monkeypatch):
    records: list[dict[str, object]] = []

    def fake_record(**kwargs):
        records.append(kwargs)
        return 1

    monkeypatch.setattr("app.sei.minuta_writer.audit.record", fake_record)
    settings = Settings(minuta_token_secret="secret-local-para-testes-com-32-caracteres")
    texto = "Texto final revisado para minuta."
    confirmation = generate_minuta_token(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        texto=texto,
        secret=settings.minuta_token_secret,
    )
    writer = MinutaWriter(
        processo_confirmado="202600000123456",
        processo_aberto="202600000123456",
        tipo_documento="Despacho",
        texto_final=texto,
        usuario_local="operador.local",
        settings=settings,
    )

    result = writer.salvar_minuta(confirmation_token=confirmation.token)

    assert result.status == "simulado"
    assert result.text_hash == text_hash(texto)
    assert records
    metadata = records[0]["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["text_hash"] == text_hash(texto)
    assert "texto" not in metadata
    assert texto not in str(records)


def test_token_falha_se_texto_mudar(monkeypatch):
    monkeypatch.setattr("app.sei.minuta_writer.audit.record", lambda **_: 1)
    settings = Settings(minuta_token_secret="secret-local-para-testes-com-32-caracteres")
    confirmation = generate_minuta_token(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        texto="Texto original.",
        secret=settings.minuta_token_secret,
    )
    writer = MinutaWriter(
        processo_confirmado="202600000123456",
        processo_aberto="202600000123456",
        tipo_documento="Despacho",
        texto_final="Texto alterado.",
        settings=settings,
    )

    with pytest.raises(PermissionError):
        writer.salvar_minuta(confirmation_token=confirmation.token)


def test_minuta_writer_confere_processo_aberto():
    with pytest.raises(ValueError, match="Processo aberto nao confere"):
        MinutaWriter(
            processo_confirmado="202600000123456",
            processo_aberto="202600000999999",
            tipo_documento="Despacho",
            texto_final="Texto.",
            settings=Settings(),
        )


def test_escrita_real_continua_not_implemented(monkeypatch):
    monkeypatch.setattr("app.sei.minuta_writer.audit.record", lambda **_: 1)
    settings = Settings(
        enable_minuta_creation=True,
        minuta_token_secret="secret-local-para-testes-com-32-caracteres",
    )
    texto = "Texto final revisado para minuta."
    confirmation = generate_minuta_token(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        texto=texto,
        secret=settings.minuta_token_secret,
    )
    writer = MinutaWriter(
        processo_confirmado="202600000123456",
        processo_aberto="202600000123456",
        tipo_documento="Despacho",
        texto_final=texto,
        settings=settings,
    )

    with pytest.raises(NotImplementedError):
        writer.salvar_minuta(confirmation_token=confirmation.token)


def test_playwright_direto_so_em_arquivo_autorizado():
    root = Path(__file__).resolve().parents[1]
    allowed = {root / "app" / "sei" / "playwright_session.py"}
    forbidden_patterns = (
        ".click(",
        ".fill(",
        ".goto(",
        ".press(",
        ".type(",
        ".set_input_files(",
        ".select_option(",
        ".dispatch_event(",
        ".evaluate(",
    )

    violations: list[str] = []
    for path in sorted((root / "app").rglob("*.py")):
        if path in allowed:
            continue
        source = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in source:
                violations.append(f"{path.relative_to(root)} contem {pattern}")

    assert violations == []
