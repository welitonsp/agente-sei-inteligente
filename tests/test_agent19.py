"""Testes do nucleo explicito do Agente 19."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent.agent19 import AgentRequest, run_agent19


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'agent19.db').as_posix()}",
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


def test_agente19_executa_ferramenta_de_missao_supervisionada(db_env):
    result = run_agent19(
        AgentRequest(
            mensagem="Analise o processo e diga o que interessa ao 19 CRPM.",
            titulo="Oficio de apoio",
            texto="Oficio solicitando apoio do 19 CRPM no prazo de 10 dias uteis.",
            processo_sei="2026.000700",
            usuario_local="operador.local",
            perfil_local="operador",
        )
    ).to_contract()

    assert result["agente"]["nome"] == "Agente 19"
    assert result["agente"]["tipo"] == "servidor_digital_ia_supervisionado"
    assert result["agente"]["intencao"] == "analisar_interesse_19crpm"
    assert result["ferramentas_usadas"][0]["ferramenta"] == "mission_control"
    assert result["ferramentas_usadas"][0]["read_only"] is True
    assert result["ferramentas_disponiveis"][0]["nome"] == "mission_control"
    assert result["trace"]["trace_id"].startswith("agt19-")
    assert result["resultado"]["mission_trace_id"] == result["trace"]["trace_id"]
    assert [step["etapa"] for step in result["trace"]["passos"]] == [
        "receber_solicitacao",
        "detectar_intencao",
        "montar_plano",
        "selecionar_ferramenta",
        "executar_ferramenta",
        "montar_resposta",
    ]
    assert result["revisao_humana_obrigatoria"] is True
    assert "ASSINAR_DOCUMENTO" in result["acoes_bloqueadas"]
    assert "Processo: 2026.000700" in result["resposta"]


def test_agente19_sem_texto_pede_complemento():
    result = run_agent19(
        AgentRequest(
            mensagem="Analise o processo para o 19 CRPM.",
            processo_sei="2026.000701",
        )
    ).to_contract()

    assert result["status"] == "precisa_complemento"
    assert result["ferramentas_usadas"] == []
    assert result["trace"]["passos"][-1]["etapa"] == "verificar_contexto"
    assert "preciso do texto" in result["resposta"].lower()


def test_agente19_aceita_trace_id_externo(db_env):
    result = run_agent19(
        AgentRequest(
            mensagem="Analise para o 19 CRPM.",
            titulo="Teste",
            texto="Oficio solicitando apoio.",
            processo_sei="2026.000702",
            trace_id="agt19-teste-manual",
        )
    ).to_contract()

    assert result["trace"]["trace_id"] == "agt19-teste-manual"
    assert result["resultado"]["mission_trace_id"] == "agt19-teste-manual"
