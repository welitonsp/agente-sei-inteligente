"""Testes da suite de avaliacao operacional do agente."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.evaluation.agent_readiness import run_agent_readiness_evals


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'agent_evals.db').as_posix()}",
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


def test_agent_readiness_evals_passam_casos_basicos(db_env):
    report = run_agent_readiness_evals()

    assert report.passed is True
    assert report.total >= 4
    assert report.failed_count == 0
    assert all(result.passed for result in report.results)
