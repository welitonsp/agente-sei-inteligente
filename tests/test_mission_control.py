"""Testes do orquestrador operacional do Agente 19."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.intelligence.mission_control import MissionRequest, execute_mission


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'mission.db').as_posix()}",
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


def test_mission_control_orquestra_analise_triagem_e_minuta(db_env):
    result = execute_mission(
        MissionRequest(
            titulo="Oficio sobre apoio operacional",
            texto=(
                "Oficio solicitando apoio operacional do 19 CRPM. "
                "Responder no prazo de 10 dias uteis."
            ),
            processo_sei="2026.000123",
            unidade_destino="PM/19 CRPM",
            usuario_local="operador.local",
            mission_trace_id="agt19-missao-teste",
        )
    )
    contract = result.to_contract()

    assert contract["status"] == "pronto_para_revisao"
    assert contract["mission_trace_id"] == "agt19-missao-teste"
    assert contract["revisao_humana_obrigatoria"] is True
    assert contract["resultado"]["prontidao_operacional"] >= 0.7
    assert contract["resultado"]["analise"]["tipo_provavel"] == "oficio"
    assert contract["resultado"]["minuta"]["texto"]
    assert "ASSINAR_DOCUMENTO" in contract["acoes_bloqueadas"]
    assert "TRAMITAR_PROCESSO" in contract["acoes_bloqueadas"]
    assert "Conferir resumo" in contract["resultado"]["plano_operacional"][0]


def test_mission_control_sem_conteudo_pede_complemento():
    result = execute_mission(MissionRequest(titulo="", texto=""))
    contract = result.to_contract()

    assert contract["status"] == "precisa_complemento"
    assert contract["resultado"]["etapa_recomendada"] == "informar_conteudo"
    assert set(contract["campos_pendentes"]) == {"titulo", "texto"}
    assert "conteudo_ausente" in contract["resultado"]["riscos"]


def test_mission_control_destaca_unidade_pendente(db_env):
    result = execute_mission(
        MissionRequest(
            titulo="Demanda administrativa",
            texto="Documento informativo para arquivo interno e leitura posterior.",
            processo_sei="2026.000124",
        )
    )
    contract = result.to_contract()

    assert contract["status"] == "precisa_complemento"
    assert "unidade_destino" in contract["campos_pendentes"]
    assert contract["resultado"]["etapa_recomendada"] == "definir_unidade_destino"
    assert "campos_pendentes" in contract["resultado"]["riscos"]
