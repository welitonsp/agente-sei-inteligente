"""Montagem do runtime de agenda: escolhe backend e resolver conforme o ambiente.

Sem credenciais OAuth completas ou com CALENDAR_BACKEND=dry_run, tudo opera em
simulacao (InMemory). Com credenciais e CALENDAR_BACKEND=google, usa Calendar
real e People API.

Esta camada e o ponto de producao que injeta o provider ICS (regra 5): o
agenda_service consulta o calendario real antes de aceitar um novo evento.
"""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.integrations import google_auth
from app.integrations.agenda_service import (
    AgendaRequest,
    AgendaResult,
    EventInput,
    create_calendar_event,
    settings_ics_provider,
)
from app.integrations.calendar_backend import (
    CalendarBackend,
    GoogleCalendarBackend,
    InMemoryCalendarBackend,
)
from app.integrations.contacts_resolver import OfficersResolver, build_resolver


def build_calendar_backend(
    settings: Settings | None = None,
    credentials: Any | None = None,
) -> CalendarBackend:
    """Backend real apenas se CALENDAR_BACKEND=google E houver credenciais."""
    s = settings or get_settings()
    if s.calendar_backend == "google" and credentials is not None:
        return GoogleCalendarBackend(credentials)
    return InMemoryCalendarBackend()  # dry-run seguro


def build_officers_resolver(
    settings: Settings | None = None,
    credentials: Any | None = None,
    static_emails: list[str] | None = None,
) -> OfficersResolver | None:
    """Resolver dos Oficiais conforme OFFICERS_SOURCE e credenciais."""
    s = settings or get_settings()
    return build_resolver(
        officers_source=s.officers_source,
        officers_contact_label=s.officers_contact_label,
        officers_group_email=s.officers_group_email,
        credentials=credentials,
        static_emails=static_emails,
    )


def schedule_official_event(
    evento: EventInput,
    *,
    processo_sei: str = "",
    usuario_local: str = "",
    aprovado_por_humano: bool = False,
    exigir_convidados: bool = True,
    contexto_observacao: dict[str, Any] | None = None,
    static_emails: list[str] | None = None,
    settings: Settings | None = None,
    ics_provider=settings_ics_provider,
) -> AgendaResult:
    """Orquestra a criacao/simulacao de um evento dos Oficiais ponta a ponta.

    1. Constroi credenciais (None -> dry-run).
    2. Escolhe backend (real ou InMemory).
    3. Resolve os e-mails dos Oficiais (marcador OFICIAIS via People API).
    4. Consulta o calendario real (ICS) para evitar duplicidade.
    5. Aplica guard (CRIAR_EVENTO_AGENDA exige aprovacao humana) e cria/simula.

    Convites reais (sendUpdates=all) so quando o backend e real.
    """
    s = settings or get_settings()
    credentials = google_auth.build_credentials(s)

    backend = build_calendar_backend(s, credentials)
    resolver = build_officers_resolver(s, credentials, static_emails=static_emails)
    convidados = resolver.resolve_emails() if resolver is not None else []

    request = AgendaRequest(
        evento=evento,
        processo_sei=processo_sei,
        convidados=convidados,
        exigir_convidados=exigir_convidados,
        enviar_convites=backend.is_real,
        contexto_observacao=contexto_observacao or {},
        usuario_local=usuario_local,
        aprovado_por_humano=aprovado_por_humano,
    )
    return create_calendar_event(
        request,
        backend,
        s.google_calendar_id,
        ics_provider=ics_provider,
    )
