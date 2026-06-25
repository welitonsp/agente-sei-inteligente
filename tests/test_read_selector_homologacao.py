"""Testes da homologação de leitura (FASE 5C - Frente 2)."""

from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.sei.read_selector_manifest import (
    REQUIRED_READ_SELECTOR_KEYS,
    evaluate_read_selector_manifest,
    load_read_selector_manifest,
)

TEMPLATE = Path("knowledge_base/sei_homologacao/read_selectors.template.json")


def _manifest_validado() -> dict:
    return {
        "version": "teste",
        "selectors": {
            k: {"value": f"#sel_{k}", "status": "validated"}
            for k in REQUIRED_READ_SELECTOR_KEYS
        },
    }


def test_template_existe_e_esta_pending():
    manifest = load_read_selector_manifest(TEMPLATE)
    report = evaluate_read_selector_manifest(manifest)
    # O template vem como candidato: nao homologado ainda.
    assert report.ok is False
    assert set(report.not_homologated) == set(REQUIRED_READ_SELECTOR_KEYS)


def test_manifesto_validado_fica_ok():
    report = evaluate_read_selector_manifest(_manifest_validado())
    assert report.ok is True
    assert report.blockers == ()


def test_seletor_ausente_vira_missing():
    manifest = _manifest_validado()
    del manifest["selectors"]["document_tree"]
    report = evaluate_read_selector_manifest(manifest)
    assert "document_tree" in report.missing
    assert report.ok is False


def test_seletor_de_leitura_nao_pode_apontar_para_ato_oficial():
    manifest = _manifest_validado()
    manifest["selectors"]["document_tree"] = {
        "value": "a[title='Assinar Documento']",
        "status": "validated",
    }
    report = evaluate_read_selector_manifest(manifest)
    assert any("proibido" in f for f in report.forbidden)
    assert report.ok is False


def test_homologacao_recusa_quando_flag_desligada():
    from scripts.homologate_read_selectors import run

    status = run(Settings(enable_sei_browser_automation=False))
    assert status == "bloqueado"
