"""Testes da skill agenda-oficiais (docs/16 - Testes de agenda)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.integrations import agenda_service as svc
from app.integrations.agenda_service import AgendaRequest, EventInput
from app.integrations.calendar_backend import InMemoryCalendarBackend
from app.integrations.ics_reader import IcsEvent

OFICIAIS = ["of1@pmgo.go.gov.br", "of2@pmgo.go.gov.br"]

# Titulo que o agenda_service constroi para _evento_valido().
TITULO_ESPERADO = "[Reuniao] Alinhamento operacional - 19 CRPM"


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    """Banco SQLite temporario, partilhado por agenda_service e audit."""
    import app.core.audit as audit  # noqa: F401
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'agenda.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    sm = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(db, "SessionLocal", sm)
    return db


def _evento_valido() -> EventInput:
    return EventInput(
        titulo="Alinhamento operacional",
        data="2026-07-01",
        horario_inicio="09:00",
        local="19 CRPM",
        tipo="reuniao",
        origem="19 CRPM",
    )


def _req(**kw) -> AgendaRequest:
    base = dict(
        evento=_evento_valido(),
        processo_sei="2026.0001",
        convidados=list(OFICIAIS),
        aprovado_por_humano=True,
    )
    base.update(kw)
    return AgendaRequest(**base)


def test_evento_sem_aprovacao_humana_pede_revisao(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(
        _req(aprovado_por_humano=False), backend, "cal_test"
    )
    assert res.pode_criar is False
    assert res.precisa_revisao is True
    assert backend.events == {}


def test_evento_aprovado_e_criado_com_convidados(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(_req(), backend, "cal_test")
    assert res.pode_criar is True
    assert res.google_event_id.startswith("mem_")
    assert res.convidados_count == 2
    assert len(backend.events) == 1
    evento = next(iter(backend.events.values()))
    assert set(evento["attendees"]) == set(OFICIAIS)
    assert evento["summary"].startswith("[Reuniao] Alinhamento operacional")


def test_sem_convidados_nao_cria_e_registra_erro(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(_req(convidados=[]), backend, "cal_test")
    assert res.pode_criar is False
    assert res.convidados_count == 0
    assert "convidados" in res.campos_pendentes
    assert backend.events == {}


def test_sem_convidados_mas_nao_exigido_cria(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(
        _req(convidados=[], exigir_convidados=False), backend, "cal_test"
    )
    assert res.pode_criar is True
    assert res.convidados_count == 0


def test_dry_run_nunca_envia_convite_real(db_env):
    backend = InMemoryCalendarBackend()  # is_real = False
    res = svc.create_calendar_event(_req(enviar_convites=True), backend, "cal_test")
    assert res.pode_criar is True
    evento = next(iter(backend.events.values()))
    # Regra 5/8: dry-run jamais envia convite, mesmo com enviar_convites=True.
    assert evento["send_invitations"] is False


def test_campos_obrigatorios_ausentes(db_env):
    backend = InMemoryCalendarBackend()
    ev = EventInput(titulo="", data="", horario_inicio="", local="")
    res = svc.create_calendar_event(
        _req(evento=ev), backend, "cal_test"
    )
    assert res.pode_criar is False
    assert set(res.campos_pendentes) == {"titulo", "data", "horario_inicio"}


def test_duplicidade_e_bloqueada(db_env):
    backend = InMemoryCalendarBackend()
    primeira = svc.create_calendar_event(_req(), backend, "cal_test")
    assert primeira.pode_criar is True
    segunda = svc.create_calendar_event(_req(), backend, "cal_test")
    assert segunda.pode_criar is False
    assert "duplic" in segunda.motivo.lower()
    assert len(backend.events) == 1


def test_convidados_sao_normalizados_e_deduplicados(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(
        _req(convidados=["A@x.com", "a@x.com ", "", "b@x.com"]),
        backend,
        "cal_test",
    )
    assert res.convidados_count == 2
    evento = next(iter(backend.events.values()))
    assert set(evento["attendees"]) == {"a@x.com", "b@x.com"}


def test_lembretes_por_tipo():
    assert svc.reminders_for("prazo") == [10080, 4320, 1440, 0]
    assert svc.reminders_for("curso") == [4320, 1440, 60]
    assert svc.reminders_for(None) == [1440, 60]
    assert svc.reminders_for("inexistente") == [1440, 60]


def test_chave_duplicidade_normaliza():
    a = svc.deduplication_key("2026.1", "Reuniao", "2026-07-01", "09:00", "19 CRPM")
    b = svc.deduplication_key("2026.1", " reuniao ", "2026-07-01", "09:00", "19 crpm")
    assert a == b


def test_fim_padrao_uma_hora_depois():
    ev = EventInput(titulo="X", data="2026-07-01", horario_inicio="09:00")
    assert svc._end_iso(ev) == "2026-07-01T10:00:00-03:00"


def _ics_equivalente() -> IcsEvent:
    return IcsEvent(
        uid="real-1",
        summary=TITULO_ESPERADO,
        dtstart_raw="20260701T090000",
        location="19 CRPM",
    )


def test_ics_vazio_permite_simular(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(
        _req(), backend, "cal_test", ics_provider=lambda: []
    )
    assert res.pode_criar is True
    assert res.status == "simulated"


def test_ics_evento_equivalente_bloqueia_como_duplicate(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(
        _req(), backend, "cal_test", ics_provider=lambda: [_ics_equivalente()]
    )
    assert res.pode_criar is False
    assert res.status == "duplicate"
    assert "calendario real" in res.motivo.lower()
    assert backend.events == {}


def test_ics_dedup_por_numero_de_processo(db_env):
    backend = InMemoryCalendarBackend()
    ics = IcsEvent(
        uid="real-2",
        summary="Outro titulo qualquer",
        dtstart_raw="20260701T090000",
        description="Refere-se ao processo 2026.0001 do 19 CRPM",
        location="19 CRPM",
    )
    res = svc.create_calendar_event(
        _req(), backend, "cal_test", ics_provider=lambda: [ics]
    )
    assert res.status == "duplicate"


def test_ics_mesmo_titulo_data_diferente_nao_bloqueia(db_env):
    backend = InMemoryCalendarBackend()
    ics = IcsEvent(
        uid="real-3",
        summary=TITULO_ESPERADO,
        dtstart_raw="20260801T090000",  # data diferente (agosto)
        location="19 CRPM",
    )
    res = svc.create_calendar_event(
        _req(), backend, "cal_test", ics_provider=lambda: [ics]
    )
    assert res.pode_criar is True
    assert res.status == "simulated"


def test_ics_falha_de_acesso_tem_fallback_seguro(db_env):
    backend = InMemoryCalendarBackend()

    def boom() -> list[IcsEvent]:
        raise RuntimeError("falha de rede no feed ICS")

    res = svc.create_calendar_event(_req(), backend, "cal_test", ics_provider=boom)
    # Fallback seguro: nao bloqueia por falha de acesso.
    assert res.pode_criar is True
    assert res.status == "simulated"


def test_settings_provider_sem_url_retorna_vazio(monkeypatch):
    """Fallback seguro quando GOOGLE_CALENDAR_ICS_URL nao esta configurada."""

    class _S:
        google_calendar_ics_url = ""

    monkeypatch.setattr(svc, "get_settings", lambda: _S())
    assert svc.settings_ics_provider() == []


def test_provider_none_pula_checagem_ics(db_env):
    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(_req(), backend, "cal_test", ics_provider=None)
    assert res.pode_criar is True
    assert res.status == "simulated"


def test_auditoria_nao_registra_emails_apenas_contagem(db_env):
    """Regra 7: o log de auditoria guarda a contagem, nunca os e-mails."""
    import app.storage.models as models

    backend = InMemoryCalendarBackend()
    res = svc.create_calendar_event(_req(), backend, "cal_test")
    assert res.pode_criar is True

    with db_env.session_scope() as s:
        todos = s.query(models.AuditLog).all()
        assert todos, "deveria existir registro de auditoria"

        # Nenhum e-mail pode aparecer em qualquer registro (regra 7).
        for row in todos:
            blob = f"{row.meta_json} {row.reason}"
            for email in OFICIAIS:
                assert email not in blob
            assert "@" not in (str(row.meta_json))

        # O registro de criacao deve conter a contagem de convidados.
        criacao = [
            r
            for r in todos
            if r.action == "CRIAR_EVENTO_AGENDA"
            and r.meta_json.get("convidados_count") is not None
        ]
        assert len(criacao) == 1
        assert criacao[0].meta_json["convidados_count"] == 2
