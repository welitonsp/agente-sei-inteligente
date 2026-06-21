"""Testa o servico de auditoria com banco SQLite em arquivo temporario."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def audit_env(tmp_path, monkeypatch):
    """Aponta o app para um banco SQLite temporario, sem recarregar modulos.

    Substitui o SessionLocal do modulo db por um vinculado a um engine novo,
    isolando o teste do banco padrao ./data.
    """
    import app.core.audit as audit
    import app.storage.db as db
    import app.storage.models as models

    db_file = tmp_path / "audit_test.db"
    engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return audit, db, models


def test_record_persiste_e_sanitiza(audit_env):
    audit, db, models = audit_env

    audit_id = audit.record(
        action="LER_DOCUMENTO",
        result="permitido",
        actor_id="servidor.local",
        target_id="2026.000123",
        reason="leitura assistida",
        metadata={"processo": "2026.000123", "senha_sei": "segredo"},
    )
    assert audit_id > 0

    with db.session_scope() as s:
        row = s.get(models.AuditLog, audit_id)
        assert row.action == "LER_DOCUMENTO"
        assert row.result == "permitido"
        # O segredo nao pode ter sido gravado.
        assert row.meta_json["senha_sei"] == "[REDACTED]"
        assert row.meta_json["processo"] == "2026.000123"


def test_record_guard_decision(audit_env):
    audit, db, models = audit_env
    from app.sei.sei_action_guard import GuardRequest, evaluate

    req = GuardRequest(
        acao_solicitada="ASSINAR_DOCUMENTO",
        usuario_local="servidor.local",
        processo_sei="2026.000123",
    )
    res = evaluate(req)
    audit_id = audit.record_guard_decision(req, res)

    with db.session_scope() as s:
        row = s.get(models.AuditLog, audit_id)
        assert row.result == "bloqueado"
        assert row.action == "ASSINAR_DOCUMENTO"
