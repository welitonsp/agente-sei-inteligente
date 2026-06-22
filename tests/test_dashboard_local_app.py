"""Testes do painel MVP local."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dashboard import local_app


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'dashboard.db').as_posix()}",
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


def test_index_tem_campos_minimos_do_checklist():
    html = local_app.INDEX_HTML

    assert 'name="processo_sei"' in html
    assert 'name="texto"' in html
    assert 'name="pdf"' in html
    assert "Analisar para o 19 CRPM" in html
    assert "Revisao humana" in html
    assert "Campos pendentes" in html
    assert "/api/import-pdf" in html


def test_create_import_text_response_retorna_resultado_estruturado(db_env):
    db, models = db_env

    response = local_app.create_import_text_response(
        {
            "titulo": "Reuniao operacional",
            "texto": "Convocacao para reuniao em 2026-07-01 as 09:00. Local: 19 CRPM.",
            "processo_sei": "2026.000126",
            "usuario_local": "operador.local",
        }
    )

    assert response["status"] == "precisa_revisao"
    assert response["revisao_humana_obrigatoria"] is True
    assert response["resultado"]["evento"]["ha_evento"] is True
    assert response["resultado"]["text_hash"]

    with db.session_scope() as session:
        assert session.query(models.Process).count() == 1
        assert session.query(models.Document).count() == 1
        assert session.query(models.AuditLog).count() >= 1


def test_create_import_text_response_nao_retorna_texto_integral(db_env):
    marcador = "NAO_RETORNAR_ESTE_TEXTO"

    response = local_app.create_import_text_response(
        {
            "titulo": "Prazo",
            "texto": f"Prazo ate 2026-07-02. {marcador}",
            "processo_sei": "2026.000127",
        }
    )

    blob = str(response)
    assert marcador not in blob
    assert response["resultado"]["text_hash"]
