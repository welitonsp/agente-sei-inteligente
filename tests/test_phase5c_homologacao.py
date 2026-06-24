"""Testes da FASE 5C-H: Coleta manual e validacao supervisionada."""

from __future__ import annotations

import ast
from pathlib import Path

from app.sei.fase5b_homologacao import evaluate_phase5b_readiness
from app.sei.minuta_cadastro import MinutaCadastro
from app.sei.selector_manifest import evaluate_selector_manifest

SCRIPT_PATH = Path("scripts/prepare_selector_homologation.py")
REPORT_TEMPLATE_PATH = Path("knowledge_base/sei_homologacao/homologacao_selectors.report.template.md")


def test_script_nao_importa_libs_de_automacao():
    """Garante que o script offline nao usa dependencias de rede ou UI."""
    assert SCRIPT_PATH.exists()
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(content)

    forbidden_imports = {"playwright", "selenium", "requests", "httpx", "urllib"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_imports, f"Import proibido encontrado: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module.split(".")[0] not in forbidden_imports, f"ImportFrom proibido encontrado: {node.module}"


def test_relatorio_template_nao_contem_dados_reais():
    """Verifica se o template de relatorio esta com placeholders."""
    assert REPORT_TEMPLATE_PATH.exists()
    content = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
    
    assert "[DD/MM/AAAA]" in content
    assert "[Nome do Desenvolvedor/Auditor]" in content
    assert "[Preencher]" in content
    # Garante que nao escapou nenhum seletor real alem do basico da tabela
    assert "12345" not in content.lower()


def test_manifesto_com_pending_continua_nao_pronto():
    """Garante que o status pending eh corretamente barrado."""
    manifest = {
        "version": "test",
        "selectors": {
            "process_number_area": {"value": "#divArvoreInformacao > a", "status": "pending"},
            "include_document_button": {"value": "img[title='Incluir Documento']", "status": "validated"},
            "document_type_search": {"value": "#txtPesquisaProcedimento", "status": "validated"},
            "document_type_option": {"value": "a.classeArvore", "status": "validated"},
            "document_description": {"value": "#txtDescricao", "status": "validated"},
            "document_access_level": {"value": "input[name='optNivelAcesso']", "status": "validated"},
            "editor_frame": {"value": "iframe#ifrEditor", "status": "validated"},
            "editor_body": {"value": "body.cke_editable", "status": "validated"},
            "save_button": {"value": "#btnSalvar", "status": "validated"},
        }
    }
    
    report = evaluate_selector_manifest(manifest)
    assert not report.ok
    assert "process_number_area" in report.not_homologated


def test_manifesto_totalmente_valido_nao_habilita_escrita_real():
    """Mesmo com tudo validated, real_write_allowed deve ser False."""
    manifest = {
        "version": "test",
        "selectors": {
            "process_number_area": {"value": "#divArvoreInformacao > a", "status": "validated"},
            "include_document_button": {"value": "img[title='Incluir Documento']", "status": "validated"},
            "document_type_search": {"value": "#txtPesquisaProcedimento", "status": "validated"},
            "document_type_option": {"value": "a.classeArvore", "status": "validated"},
            "document_description": {"value": "#txtDescricao", "status": "validated"},
            "document_access_level": {"value": "input[name='optNivelAcesso']", "status": "validated"},
            "editor_frame": {"value": "iframe#ifrEditor", "status": "validated"},
            "editor_body": {"value": "body.cke_editable", "status": "validated"},
            "save_button": {"value": "#btnSalvar", "status": "validated"},
        }
    }
    
    report = evaluate_selector_manifest(manifest)
    assert report.ok
    
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
    )
    
    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=manifest
    )
    
    assert readiness.ready_for_homologation is True
    # GARANTIA ABSOLUTA DE QUE NAO ESTA AUTORIZANDO ESCRITA:
    assert readiness.real_write_allowed is False
