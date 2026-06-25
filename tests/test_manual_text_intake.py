"""Testes do fluxo IMPORT_TEXT do MVP externo/local."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.intake.manual_text import (
    ManualTextRequest,
    analyze_text,
    extract_deadline,
    extract_event,
)


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'manual_text.db').as_posix()}",
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


def test_import_text_persiste_metadados_sem_texto_integral(db_env):
    db, models = db_env
    marcador_sensivel = "TRECHO_SIGILOSO_NAO_DEVE_SER_PERSISTIDO"
    texto = (
        "Convocacao para reuniao operacional em 2026-07-01 as 09:00. "
        "Local: 19 CRPM. "
        f"{marcador_sensivel}"
    )

    result = analyze_text(
        ManualTextRequest(
            titulo="Reuniao operacional",
            texto=texto,
            processo_sei="2026.000123",
            usuario_local="servidor.local",
            estacao="estacao-01",
        )
    )

    assert result.status == "precisa_revisao"
    assert result.revisao_humana_obrigatoria is True
    assert result.text_hash
    assert result.evento.ha_evento is True
    assert result.evento.data == "2026-07-01"
    assert result.evento.horario_inicio == "09:00"
    assert result.evento.local == "19 CRPM"
    assert marcador_sensivel not in result.resumo_executivo

    with db.session_scope() as session:
        process = session.get(models.Process, result.processo_id)
        document = session.get(models.Document, result.documento_id)
        assert process.sei_number == "2026.000123"
        assert document.source_type == "texto"
        assert document.text_hash == result.text_hash
        assert document.extracted_text_path is None
        assert document.classification == "texto_manual"
        assert marcador_sensivel not in (document.summary or "")


def test_auditoria_nao_grava_texto_colado(db_env):
    db, models = db_env
    marcador_sensivel = "CONTEUDO_COMPLETO_DO_DOCUMENTO"

    result = analyze_text(
        ManualTextRequest(
            titulo="Prazo administrativo",
            texto=f"Ha prazo para resposta ate 02/07/2026. {marcador_sensivel}",
            processo_sei="2026.000124",
            usuario_local="servidor.local",
        )
    )

    with db.session_scope() as session:
        logs = session.query(models.AuditLog).all()
        assert len(logs) == len(result.audit_log_ids)
        for row in logs:
            blob = f"{row.reason} {row.meta_json}"
            assert marcador_sensivel not in blob
            assert "texto" not in (row.meta_json or {})
        assert any((row.meta_json or {}).get("modo_leitura") == "texto_colado" for row in logs)


def test_texto_ausente_nao_cria_documento(db_env):
    db, models = db_env

    result = analyze_text(
        ManualTextRequest(
            titulo="Sem texto",
            texto="   ",
            processo_sei="2026.000125",
            usuario_local="servidor.local",
        )
    )

    assert result.status == "precisa_revisao"
    assert result.documento_id is None
    assert "texto" in result.campos_pendentes

    with db.session_scope() as session:
        assert session.query(models.Document).count() == 0
        assert session.query(models.Process).count() == 0
        assert session.query(models.AuditLog).count() == 1


def test_extract_event_marca_campos_pendentes():
    event = extract_event("Convocacao para reuniao no auditorio.", "Reuniao")

    assert event.ha_evento is False
    assert event.titulo == "Reuniao"
    assert set(event.campos_pendentes) == {"data", "horario_inicio", "local"}
    assert event.agenda_sugerida is False


def test_extract_deadline_converte_data_brasileira():
    deadline = extract_deadline("Prazo urgente para responder ate 02/07/2026 as 17h30.")

    assert deadline.ha_prazo is True
    assert deadline.data_limite == "2026-07-02"
    assert deadline.hora_limite == "17:30"
    assert deadline.risco == "urgente"
    assert deadline.lembretes_sugeridos == [1440, 0]


def test_extract_deadline_detecta_prazo_relativo():
    # Caso real do SEI: "no prazo de 10 dias uteis" sem data escrita.
    from datetime import date

    deadline = extract_deadline(
        "Responder no prazo de 10 (dez) dias uteis.",
        reference_date=date(2026, 6, 24),
    )
    assert deadline.ha_prazo is True
    assert deadline.tipo_prazo == "relativo"
    # 24/06/2026 (quarta) + 10 dias uteis -> 08/07/2026.
    assert deadline.data_limite == "2026-07-08"
