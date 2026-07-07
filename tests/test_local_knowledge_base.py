"""Testes da knowledge base local do 19 CRPM."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.intelligence.knowledge_base import load_knowledge_base
from app.intelligence.local_triage import TriageRequest, analyze_triage


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'kb.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return db, models


def _write_kb(base: Path, *, invalid_unit: bool = False) -> None:
    base.mkdir(parents=True)
    (base / "unidades_19crpm.csv").write_text(
        "codigo,nome,tipo,ativo,observacao\n"
        "u1,PM/19 CRPM,operacional,true,fixture\n",
        encoding="utf-8",
    )
    (base / "unidades_alto_comando.csv").write_text(
        "codigo,nome,tipo,ativo,observacao\n",
        encoding="utf-8",
    )
    (base / "palavras_chave_19crpm.csv").write_text(
        "termo,categoria,peso,interesse,ativo,observacao\n"
        "apoio administrativo,administrativo,5,direto,true,fixture\n",
        encoding="utf-8",
    )
    unidade = "UNIDADE INEXISTENTE" if invalid_unit else "PM/19 CRPM"
    (base / "regras_direcionamento.csv").write_text(
        "id,termos,unidade_destino,tipo_minuta,providencia,interesse,prioridade,confianca,ativo,observacao\n"
        f"r1,apoio administrativo;atividade institucional,{unidade},despacho,"
        "encaminhar para providencias,direto,90,0.74,true,fixture\n",
        encoding="utf-8",
    )


def test_load_empty_knowledge_base_nao_tem_regras_reais(tmp_path):
    base = tmp_path / "kb"
    base.mkdir()

    kb = load_knowledge_base(base)

    assert kb.has_real_rules is False
    assert kb.unidades_19crpm == ()
    assert kb.regras_direcionamento == ()


def test_triage_sem_regras_nao_inventa_unidade(db_env, tmp_path):
    base = tmp_path / "kb"
    base.mkdir()

    result = analyze_triage(
        TriageRequest(
            assunto="Apoio administrativo",
            texto="Solicitacao de apoio administrativo.",
            processo_sei="2026.000400",
            kb_path=base,
        )
    )

    assert result.status == "precisa_revisao"
    assert result.interesse_19crpm == "indefinido"
    assert result.unidade_sugerida == ""
    assert "knowledge_base_regras" in result.campos_pendentes
    assert result.revisao_humana_obrigatoria is True


def test_triage_com_regra_ficticia_sugere_unidade_e_minuta(db_env, tmp_path):
    base = tmp_path / "kb"
    _write_kb(base)

    result = analyze_triage(
        TriageRequest(
            assunto="Apoio administrativo para atividade institucional",
            texto="Solicita apoio administrativo para atividade institucional.",
            processo_sei="2026.000401",
            kb_path=base,
        )
    )

    assert result.status == "precisa_revisao"
    assert result.interesse_19crpm == "direto"
    assert result.unidade_sugerida == "PM/19 CRPM"
    assert result.tipo_minuta_sugerido == "despacho"
    assert result.regra_aplicada == "r1"
    assert result.evidencias == ["apoio administrativo", "atividade institucional"]
    assert result.confianca == 0.74


def test_triage_com_unidade_nao_cadastrada_nao_sugere_unidade(db_env, tmp_path):
    base = tmp_path / "kb"
    _write_kb(base, invalid_unit=True)

    result = analyze_triage(
        TriageRequest(
            assunto="Apoio administrativo",
            texto="Solicitacao de apoio administrativo.",
            kb_path=base,
        )
    )

    assert result.unidade_sugerida == ""
    assert "unidade_destino_nao_cadastrada" in result.campos_pendentes
    assert result.confianca <= 0.45


def test_triage_default_kb_aplica_regra_conservadora_19crpm(db_env):
    result = analyze_triage(
        TriageRequest(
            assunto="Apoio operacional ao 19º CRPM",
            texto=(
                "Processo solicita apoio operacional ao 19º CRPM para "
                "policiamento em evento institucional."
            ),
            processo_sei="2026.000402",
            usuario_local="operador.local",
        )
    )

    assert result.status == "precisa_revisao"
    assert result.interesse_19crpm == "direto"
    assert result.unidade_sugerida == "PM/19 CRPM"
    assert result.tipo_minuta_sugerido == "despacho"
    assert result.regra_aplicada == "r19_mencao_direta"
    assert "19º crpm" in result.evidencias
    assert result.confianca == 0.82
    assert result.revisao_humana_obrigatoria is True
