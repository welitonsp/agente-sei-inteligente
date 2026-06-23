"""Contratos da FASE 5B em modo homologacao."""

from __future__ import annotations

from app.sei.fase5b_homologacao import evaluate_phase5b_readiness
from app.sei.minuta_cadastro import MinutaCadastro, validate_minuta_cadastro
from app.sei.selector_manifest import evaluate_selector_manifest


def _valid_manifest() -> dict:
    return {
        "version": "teste",
        "selectors": {
            "abrir_incluir_documento": {"value": "#incluir", "status": "homologado"},
            "selecionar_tipo_documento": {"value": "#tipo", "status": "homologado"},
            "campo_descricao": {"value": "#descricao", "status": "homologado"},
            "campo_interessado": {"value": "#interessado", "status": "homologado"},
            "campo_destinatario": {"value": "#destinatario", "status": "homologado"},
            "campo_nivel_acesso": {"value": "#nivel", "status": "homologado"},
            "editor_texto": {"value": "#editor", "status": "homologado"},
            "salvar_minuta": {"value": "#salvar", "status": "homologado"},
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
    manifest["selectors"]["editor_texto"]["status"] = "pendente"

    report = evaluate_selector_manifest(manifest)

    assert not report.ok
    assert "editor_texto" in report.not_homologated


def test_manifesto_bloqueia_termos_de_ato_oficial():
    manifest = _valid_manifest()
    manifest["selectors"]["assinar_documento"] = {
        "value": "#assinar",
        "status": "homologado",
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
            "abrir_incluir_documento": {"value": "", "status": "pendente"},
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
    assert "abrir_incluir_documento" in readiness.blockers
