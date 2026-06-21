"""Backends de calendario para a skill `agenda-oficiais`.

Abstrai a criacao de eventos para que a logica de negocio (agenda_service)
seja testavel sem credenciais Google. Dois backends:

- InMemoryCalendarBackend: usado em testes e em modo dry-run do MVP.
- GoogleCalendarBackend: integracao real (import tardio das libs Google).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class CalendarEvent:
    """Representacao neutra de um evento a ser criado no calendario."""

    summary: str
    start: str  # ISO 8601 com timezone, ex: 2026-07-01T09:00:00-03:00
    end: str
    location: str = ""
    description: str = ""
    attendees: list[str] = field(default_factory=list)
    reminders_minutes: list[int] = field(default_factory=list)


class CalendarBackend(Protocol):
    def create_event(
        self,
        calendar_id: str,
        event: CalendarEvent,
        send_invitations: bool = False,
    ) -> str:
        """Cria o evento e devolve o id externo. Levanta em caso de falha.

        send_invitations: True dispara convite real aos attendees (modo real).
        """
        ...

    @property
    def is_real(self) -> bool:
        """True se o backend efetivamente envia para um servico externo."""
        ...


class InMemoryCalendarBackend:
    """Backend de dry-run: guarda eventos em memoria, sem rede nem convites."""

    is_real = False

    def __init__(self) -> None:
        self.events: dict[str, dict[str, Any]] = {}

    def create_event(
        self,
        calendar_id: str,
        event: CalendarEvent,
        send_invitations: bool = False,
    ) -> str:
        event_id = f"mem_{uuid.uuid4().hex[:12]}"
        self.events[event_id] = {
            "calendar_id": calendar_id,
            "summary": event.summary,
            "start": event.start,
            "end": event.end,
            "location": event.location,
            "description": event.description,
            "attendees": list(event.attendees),
            "reminders_minutes": list(event.reminders_minutes),
            # Em dry-run nunca se envia convite, mesmo se solicitado.
            "send_invitations": False,
        }
        return event_id


class GoogleCalendarBackend:
    """Integracao real com a Google Calendar API.

    As bibliotecas Google sao importadas de forma tardia para nao serem
    dependencia obrigatoria do nucleo nem dos testes.
    """

    is_real = True

    def __init__(self, credentials: Any) -> None:
        self._credentials = credentials

    def _service(self) -> Any:
        try:
            from googleapiclient.discovery import build  # type: ignore
        except ImportError as exc:  # pragma: no cover - depende de extra opcional
            raise RuntimeError(
                "Integracao Google requer 'google-api-python-client'. "
                "Instale o extra de agenda antes de usar GoogleCalendarBackend."
            ) from exc
        return build("calendar", "v3", credentials=self._credentials)

    def create_event(
        self,
        calendar_id: str,
        event: CalendarEvent,
        send_invitations: bool = False,
    ) -> str:  # pragma: no cover - requer rede/credenciais
        body = {
            "summary": event.summary,
            "location": event.location,
            "description": event.description,
            "start": {"dateTime": event.start},
            "end": {"dateTime": event.end},
            "attendees": [{"email": a} for a in event.attendees],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": m}
                    for m in event.reminders_minutes
                ],
            },
        }
        # Regra 5: sendUpdates="all" apenas em modo real com envio solicitado.
        send_updates = "all" if send_invitations else "none"
        created = (
            self._service()
            .events()
            .insert(calendarId=calendar_id, body=body, sendUpdates=send_updates)
            .execute()
        )
        return created["id"]
