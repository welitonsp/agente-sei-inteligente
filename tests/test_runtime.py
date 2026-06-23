"""Testes da montagem de runtime (backend/resolver) e orquestracao."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.integrations import runtime
from app.integrations.agenda_service import EventInput
from app.integrations.calendar_backend import (
    GoogleCalendarBackend,
    InMemoryCalendarBackend,
)
from app.integrations.contacts_resolver import (
    GoogleContactsResolver,
    GroupEmailResolver,
)


class _Settings:
    def __init__(self, **kw):
        self.calendar_backend = kw.get("calendar_backend", "dry_run")
        self.officers_source = kw.get("officers_source", "google_contacts")
        self.officers_contact_label = kw.get("officers_contact_label", "OFICIAIS")
        self.officers_group_email = kw.get("officers_group_email", "")
        self.google_calendar_id = kw.get("google_calendar_id", "cal_x")


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'rt.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False)
    )
    return db


def test_backend_dry_run_sem_credenciais():
    b = runtime.build_calendar_backend(_Settings(calendar_backend="google"), None)
    assert isinstance(b, InMemoryCalendarBackend)
    assert b.is_real is False


def test_backend_real_com_google_e_credenciais():
    b = runtime.build_calendar_backend(
        _Settings(calendar_backend="google"), credentials=object()
    )
    assert isinstance(b, GoogleCalendarBackend)
    assert b.is_real is True


def test_backend_dry_run_quando_flag_dry_run_mesmo_com_credenciais():
    b = runtime.build_calendar_backend(
        _Settings(calendar_backend="dry_run"), credentials=object()
    )
    assert isinstance(b, InMemoryCalendarBackend)


def test_resolver_google_contacts_sem_credenciais_e_none():
    r = runtime.build_officers_resolver(_Settings(), credentials=None)
    assert r is None


def test_resolver_google_contacts_com_credenciais():
    r = runtime.build_officers_resolver(_Settings(), credentials=object())
    assert isinstance(r, GoogleContactsResolver)


def test_resolver_group_email():
    r = runtime.build_officers_resolver(
        _Settings(officers_source="group_email", officers_group_email="g@x.com")
    )
    assert isinstance(r, GroupEmailResolver)
    assert r.resolve_emails() == ["g@x.com"]


def test_schedule_dry_run_simula_com_static_emails(db_env, monkeypatch):
    # Sem credenciais -> dry-run; usa static_emails para simular convidados.
    monkeypatch.setattr(runtime.google_auth, "build_credentials", lambda s: None)
    ev = EventInput(
        titulo="Reuniao", data="2026-07-01", horario_inicio="09:00",
        local="19 CRPM", tipo="reuniao", origem="19 CRPM",
    )
    res = runtime.schedule_official_event(
        ev,
        processo_sei="2026.0001",
        aprovado_por_humano=True,
        static_emails=["of1@x.com", "of2@x.com"],
        settings=_Settings(),
        ics_provider=lambda: [],
    )
    assert res.pode_criar is True
    assert res.status == "simulated"
    assert res.convidados_count == 2


def test_schedule_sem_convidados_em_dry_run_bloqueia(db_env, monkeypatch):
    monkeypatch.setattr(runtime.google_auth, "build_credentials", lambda s: None)
    ev = EventInput(
        titulo="Reuniao", data="2026-07-01", horario_inicio="09:00", tipo="reuniao",
    )
    res = runtime.schedule_official_event(
        ev,
        aprovado_por_humano=True,
        settings=_Settings(),  # google_contacts sem creds -> resolver None
        ics_provider=lambda: [],
    )
    assert res.pode_criar is False
    assert res.status == "sem_convidados"
