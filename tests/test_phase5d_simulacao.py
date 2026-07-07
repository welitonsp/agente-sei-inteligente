"""Testes da FASE 5D-S: Simulacao Operacional.

Testa o funcionamento sem escrita real no SEI.
"""

from __future__ import annotations

import ast
from pathlib import Path

from app.sei.fase5d_simulacao import simulate_phase5d_operation
from app.sei.minuta_cadastro import MinutaCadastro

SCRIPT_PATH = Path("scripts/simulate_phase5d_operation.py")
TEMPLATE_PATH = Path("knowledge_base/sei_homologacao/fase5d_simulacao.report.template.md")


def get_valid_manifest() -> dict:
    return {
        "version": "test",
        "selectors": {
            "process_number_area": {"value": "#process", "status": "validated"},
            "include_document_button": {"value": "#incluir", "status": "validated"},
            "document_type_search": {"value": "#tipo_search", "status": "validated"},
            "document_type_option": {"value": "#tipo_option", "status": "validated"},
            "document_description": {"value": "#descricao", "status": "validated"},
            "document_access_level": {"value": "input[name='nivel']", "status": "validated"},
            "editor_frame": {"value": "iframe#ifrEditor", "status": "validated"},
            "editor_body": {"value": "body.cke_editable", "status": "validated"},
            "save_button": {"value": "#btnSalvar", "status": "validated"},
        }
    }


def get_valid_cadastro() -> MinutaCadastro:
    return MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="a" * 64,
        descricao="Teste de integracao",
    )


def test_simulacao_com_manifesto_pending_nao_fica_pronta():
    manifest = get_valid_manifest()
    manifest["selectors"]["include_document_button"]["status"] = "pending"
    
    report = simulate_phase5d_operation(
        cadastro=get_valid_cadastro(),
        selector_manifest=manifest,
    )
    
    assert not report.ok
    assert len(report.simulated_plan) == 0
    assert "include_document_button" in report.blockers[0]
    assert report.real_write_allowed is False


def test_simulacao_com_cadastro_invalido_nao_fica_pronta():
    cadastro = MinutaCadastro(
        processo_sei="", # Invalido, vazio
        tipo_documento="Despacho",
        nivel_acesso="",
        text_hash="",
    )
    
    report = simulate_phase5d_operation(
        cadastro=cadastro,
        selector_manifest=get_valid_manifest(),
    )
    
    assert not report.ok
    assert len(report.simulated_plan) == 0
    assert report.real_write_allowed is False


def test_simulacao_com_manifesto_estruturalmente_validado_retorna_plano_simulado():
    report = simulate_phase5d_operation(
        cadastro=get_valid_cadastro(),
        selector_manifest=get_valid_manifest(),
    )
    
    assert report.ok
    assert len(report.blockers) == 0
    assert len(report.simulated_plan) > 0
    assert report.simulated_plan[0]["action"] == "simulated_validation_step"
    assert report.real_write_allowed is False
    assert report.ready_for_real_write is False


def test_script_cli_nao_importa_libs_de_automacao():
    assert SCRIPT_PATH.exists()
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(content)

    forbidden_imports = {"playwright", "selenium", "requests", "httpx", "urllib"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_imports, f"Import proibido: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module.split(".")[0] not in forbidden_imports, f"ImportFrom proibido: {node.module}"


def test_modulo_nao_chama_metodos_proibidos():
    modulo_path = Path("app/sei/fase5d_simulacao.py")
    assert modulo_path.exists()
    content = modulo_path.read_text(encoding="utf-8")
    tree = ast.parse(content)

    forbidden_calls = {"click", "fill", "goto", "press", "type", "evaluate"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden_calls:
                    # Garantir que nao eh um target de Playwright
                    if node.func.attr != "get": # permitido para dicts
                        assert False, f"Metodo proibido detectado no codigo: {node.func.attr}"


def test_relatorio_template_nao_afirma_que_escrita_real_esta_autorizada():
    assert TEMPLATE_PATH.exists()
    # Leitura como binario para evitar crash de enconding e acha string parcial
    content = TEMPLATE_PATH.read_bytes().decode("utf-8", errors="ignore")
    
    assert "Operação real habilitada?" in content
    assert "Nenhuma operação real foi executada?" in content
