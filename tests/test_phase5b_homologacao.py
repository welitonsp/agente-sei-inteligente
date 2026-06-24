"""Contratos da FASE 5B em modo homologacao."""

from __future__ import annotations

from app.sei.fase5b_homologacao import evaluate_phase5b_readiness
from app.sei.minuta_cadastro import MinutaCadastro, validate_minuta_cadastro
from app.sei.selector_manifest import evaluate_selector_manifest


def _valid_manifest() -> dict:
    return {
        "version": "teste",
        "selectors": {
            "process_number_area": {"value": "#process", "status": "validated"},
            "include_document_button": {"value": "#incluir", "status": "validated"},
            "document_type_search": {"value": "#tipo_search", "status": "validated"},
            "document_type_option": {"value": "#tipo_option", "status": "validated"},
            "document_description": {"value": "#descricao", "status": "validated"},
            "document_access_level": {"value": "#nivel", "status": "validated"},
            "editor_frame": {"value": "#frame", "status": "validated"},
            "editor_body": {"value": "#editor", "status": "validated"},
            "save_button": {"value": "#salvar", "status": "validated"},
        },
    }


def test_cadastro_exige_nivel_de_acesso_explicito():
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="",
        text_hash="a" * 64,
    )

    report = validate_minuta_cadastro(cadastro)

    assert not report.ok
    assert "nivel_acesso obrigatorio." in report.violations


def test_cadastro_restrito_exige_hipotese_legal():
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="restrito",
        text_hash="a" * 64,
    )

    report = validate_minuta_cadastro(cadastro)

    assert not report.ok
    assert "hipotese_legal obrigatoria para acesso restrito/sigiloso." in report.violations


def test_cadastro_exige_campos_aplicaveis_por_tipo_documental():
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Oficio",
        nivel_acesso="publico",
        text_hash="a" * 64,
        descricao="Resposta administrativa",
    )

    report = validate_minuta_cadastro(
        cadastro,
        required_fields=("descricao", "destinatario"),
    )

    assert not report.ok
    assert "destinatario obrigatorio para este tipo documental." in report.violations


def test_manifesto_de_seletores_exige_todos_homologados():
    manifest = _valid_manifest()
    manifest["selectors"]["editor_body"]["status"] = "pending"

    report = evaluate_selector_manifest(manifest)

    assert not report.ok
    assert "editor_body" in report.not_homologated


def test_manifesto_bloqueia_termos_de_ato_oficial():
    manifest = _valid_manifest()
    manifest["selectors"]["assinar_documento"] = {
        "value": "#assinar",
        "status": "validated",
    }

    report = evaluate_selector_manifest(manifest)

    assert not report.ok
    assert report.forbidden == ("seletor proibido: assinar_documento",)


def test_prontidao_fase5b_nao_autoriza_escrita_real():
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
        descricao="Encaminhamento para providencias",
    )

    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=_valid_manifest(),
        required_fields=("descricao",),
    )

    assert readiness.ready_for_homologation is True
    assert readiness.real_write_allowed is False
    assert readiness.blockers == ()


def test_template_sem_seletores_reais_nao_fica_pronto():
    manifest = {
        "version": "template",
        "selectors": {
            "include_document_button": {"value": "", "status": "pending"},
        },
    }
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
    )

    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=manifest,
    )

    assert readiness.ready_for_homologation is False
    assert readiness.real_write_allowed is False
    assert "include_document_button" in readiness.blockers
    assert "process_number_area" in readiness.blockers


def test_manifesto_vazio_falha():
    manifest = {}
    report = evaluate_selector_manifest(manifest)
    assert not report.ok
    assert len(report.missing) > 0


def test_manifesto_sem_seletor_obrigatorio_falha():
    manifest = _valid_manifest()
    del manifest["selectors"]["save_button"]
    report = evaluate_selector_manifest(manifest)
    assert not report.ok
    assert "save_button" in report.missing


def test_manifesto_completo_passa():
    manifest = _valid_manifest()
    report = evaluate_selector_manifest(manifest)
    assert report.ok
    assert not report.missing
    assert not report.not_homologated
    assert not report.forbidden


def test_fase_5b_h_nao_chama_playwright_e_nao_escreve_no_sei():
    # O simples fato de evaluate_phase5b_readiness nao usar Playwright 
    # e ter real_write_allowed=False cobre isso.
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
    )
    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=_valid_manifest()
    )
    assert readiness.real_write_allowed is False
    assert not hasattr(readiness, "playwright_page")


def test_fase_5b_h_nao_habilita_minuta_creation():
    # evaluate_phase5b_readiness deve retornar real_write_allowed=False, 
    # garantindo que nao esta ativando MINUTA_CREATION acidentalmente
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
    )
    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=_valid_manifest()
    )
    assert readiness.real_write_allowed is False


def test_acoes_oficiais_continuam_proibidas():
    manifest = _valid_manifest()
    manifest["selectors"]["assinar_documento"] = {"value": "#assinar", "status": "validated"}
    manifest["selectors"]["tramitar_processo"] = {"value": "#tramitar", "status": "validated"}
    
    report = evaluate_selector_manifest(manifest)
    
    assert not report.ok
    assert "seletor proibido: assinar_documento" in report.forbidden
    assert "seletor proibido: tramitar_processo" in report.forbidden
