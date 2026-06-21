"""Valida as credenciais OAuth em modo SOMENTE LEITURA (nao cria nada).

Confere:
1. Credenciais OAuth presentes e renovaveis.
2. People API: localiza o marcador OFICIAIS e conta os e-mails (sem exibi-los).
3. Calendar API: confirma acesso de leitura a agenda configurada.

Uso:
    ! .venv/Scripts/python.exe scripts/google_validate.py
"""

from __future__ import annotations

import sys

from app.core.config import get_settings
from app.integrations import google_auth
from app.integrations.contacts_resolver import GoogleContactsResolver


def main() -> int:
    s = get_settings()

    if not google_auth.is_configured(s):
        print("ERRO: credenciais OAuth incompletas no .env "
              "(GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN).")
        return 1

    creds = google_auth.build_credentials(s)
    print("[1/3] Credenciais construidas. Renovando access token...")
    try:
        from google.auth.transport.requests import Request  # type: ignore

        creds.refresh(Request())
        print("      OK: access token obtido.")
    except Exception as exc:
        print(f"      FALHA ao renovar token: {type(exc).__name__}: {exc}")
        return 1

    # 2) People API - conta convidados do marcador (sem exibir e-mails).
    print(f"[2/3] People API: procurando marcador '{s.officers_contact_label}'...")
    try:
        resolver = GoogleContactsResolver(creds, s.officers_contact_label)
        emails = resolver.resolve_emails()
        print(f"      OK: {len(emails)} e-mail(s) encontrado(s) no marcador.")
        if not emails:
            print("      ATENCAO: nenhum e-mail. Verifique o marcador e os contatos.")
    except Exception as exc:
        print(f"      FALHA People API: {type(exc).__name__}: {exc}")
        return 1

    # 3) Calendar API - acesso de leitura (events.list), sem criar nada.
    print(f"[3/3] Calendar API: lendo agenda '{s.google_calendar_id}'...")
    try:
        from googleapiclient.discovery import build  # type: ignore

        service = build("calendar", "v3", credentials=creds)
        resp = (
            service.events()
            .list(calendarId=s.google_calendar_id, maxResults=1)
            .execute()
        )
        print(f"      OK: acesso confirmado (itens lidos: {len(resp.get('items', []))}).")
    except Exception as exc:
        print(f"      FALHA Calendar API: {type(exc).__name__}: {exc}")
        return 1

    print("\n=== VALIDACAO CONCLUIDA: credenciais OK para Calendar + People. ===")
    print("Nada foi criado, alterado ou enviado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
