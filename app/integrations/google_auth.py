"""Credenciais OAuth do Google para Calendar (escrita) e People (leitura).

Escopos minimos:
- calendar.events    -> criar/atualizar eventos na agenda
- contacts.readonly  -> ler o marcador "OFICIAIS" e extrair e-mails

Seguranca:
- O refresh token e um SEGREDO; vem apenas do .env local (GOOGLE_REFRESH_TOKEN),
  nunca versionado nem logado.
- O agente nao armazena senha; o consentimento OAuth e feito uma vez pelo
  responsavel (scripts/google_oauth_setup.py) e gera o refresh token.
- Sem credenciais completas, build_credentials devolve None -> mantem dry-run.
"""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/contacts.readonly",
]

TOKEN_URI = "https://oauth2.googleapis.com/token"


def is_configured(settings: Settings | None = None) -> bool:
    """True se houver client_id, client_secret e refresh_token no ambiente."""
    s = settings or get_settings()
    return bool(
        s.google_client_id and s.google_client_secret and s.google_refresh_token
    )


def build_credentials(settings: Settings | None = None) -> Any | None:
    """Constroi as credenciais OAuth a partir do .env.

    Devolve None (fallback dry-run) se a configuracao estiver incompleta.
    A construcao e offline; a renovacao do access token ocorre de forma
    automatica na primeira chamada de API, usando o refresh token.
    """
    s = settings or get_settings()
    if not is_configured(s):
        return None

    try:
        from google.oauth2.credentials import Credentials  # type: ignore
    except ImportError as exc:  # pragma: no cover - extra opcional
        raise RuntimeError(
            "OAuth Google requer 'google-auth'. Instale os extras de Google."
        ) from exc

    return Credentials(
        token=None,
        refresh_token=s.google_refresh_token,
        client_id=s.google_client_id,
        client_secret=s.google_client_secret,
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
