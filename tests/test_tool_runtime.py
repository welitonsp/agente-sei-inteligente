"""Testes do runtime de ferramentas guardado (agente tipo n8n, porem seguro)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent.tool_runtime import (
    ExecutableTool,
    PlanStep,
    ToolRuntime,
    build_default_registry,
    run_plan,
)
from app.core.permissions import Action


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'tools.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return db


# --- catalogo / formato LLM --------------------------------------------------


def test_registry_padrao_tem_ferramentas_seguras():
    reg = build_default_registry()
    assert "consultar_manuais" in reg
    assert "gerar_minuta" in reg
    # Nenhuma ferramenta perigosa esta na allow-list.
    perigosas = {"assinar", "tramitar", "enviar_processo", "excluir", "dar_ciencia"}
    assert not (perigosas & set(reg))


def test_list_for_llm_tem_formato_claude():
    rt = ToolRuntime()
    tools = rt.list_for_llm()
    assert tools
    for t in tools:
        assert set(t) == {"name", "description", "input_schema"}
        assert t["input_schema"]["type"] == "object"


# --- allow-list / default-deny ----------------------------------------------


def test_ferramenta_desconhecida_e_negada(db_env):
    rt = ToolRuntime()
    r = rt.invoke("assinar_documento", {"x": 1})
    assert r.status == "negado"
    assert "allow-list" in r.motivo.lower()


def test_ferramenta_com_acao_proibida_e_negada_pelo_guard(db_env):
    # Uma ferramenta cujo handler nunca deveria rodar porque a acao e proibida.
    perigosa = ExecutableTool(
        nome="tramitar",
        descricao="deveria ser barrada",
        acao=Action.TRAMITAR_PROCESSO,
        input_schema={"type": "object", "properties": {}},
        handler=lambda args: {"executou": True},  # nao pode ser chamado
    )
    rt = ToolRuntime(registry={"tramitar": perigosa})
    r = rt.invoke("tramitar", {})
    assert r.status == "negado"
    assert r.output == {}  # handler nunca executou


# --- execucao real -----------------------------------------------------------


def test_consultar_manuais_retorna_contexto(db_env):
    rt = ToolRuntime()
    r = rt.invoke("consultar_manuais", {"consulta": "nivel de acesso sigiloso"})
    assert r.ok
    assert "REGRAS DOS MANUAIS" in r.output["contexto"]


def test_gerar_minuta_passa_pelo_guard_e_gera(db_env):
    rt = ToolRuntime()
    r = rt.invoke(
        "gerar_minuta",
        {"assunto": "Apoio operacional", "tipo_minuta": "despacho", "processo_sei": "2026.1"},
        usuario_local="operador",
    )
    assert r.ok
    assert r.output["resultado"]["texto"]
    assert r.output["revisao_humana_obrigatoria"] is True


def test_avaliar_redacao_integra_policy(db_env):
    rt = ToolRuntime()
    minuta = "DESPACHO\n\nProcesso SEI: 2026.1\nAssunto: x\n\nAssino e tramito o processo."
    r = rt.invoke("avaliar_redacao", {"texto": minuta, "tipo_minuta": "despacho"})
    assert r.ok
    assert r.output["bloqueado"] is True  # promessa de ato proibido


def test_handler_que_falha_vira_status_erro(db_env):
    boom = ExecutableTool(
        nome="analisar_processo",
        descricao="handler quebrado",
        acao=Action.RESUMIR,
        input_schema={"type": "object", "properties": {}},
        handler=lambda args: (_ for _ in ()).throw(RuntimeError("falhou")),
    )
    rt = ToolRuntime(registry={"analisar_processo": boom})
    r = rt.invoke("analisar_processo", {})
    assert r.status == "erro"
    assert "falhou" in r.motivo


# --- plano (workflow) --------------------------------------------------------


def test_run_plan_executa_em_sequencia_e_coleta_tudo(db_env):
    plano = [
        PlanStep("analisar_processo", {"texto": "Oficio solicita apoio com prazo de 5 dias."}),
        PlanStep("consultar_manuais", {"consulta": "minuta e assinatura"}),
        PlanStep("ferramenta_inexistente", {}),  # deve ser negada, sem parar o plano
    ]
    resultados = run_plan(plano, usuario_local="op", processo_sei="2026.9")
    assert [r.status for r in resultados] == ["ok", "ok", "negado"]
