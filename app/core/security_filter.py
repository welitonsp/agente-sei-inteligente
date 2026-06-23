"""Sanitizacao de dados sensiveis antes de qualquer log, auditoria ou envio.

Politica (docs/20 e docs/25): o agente NUNCA registra senha, cookie, token de
sessao, credencial pessoal, HTML completo com sessao ou cabecalhos de
autenticacao. Este modulo e a barreira tecnica que garante isso.
"""

from __future__ import annotations

from typing import Any

# Chaves que jamais podem ser persistidas. Comparacao por substring, case-insensitive.
FORBIDDEN_KEY_FRAGMENTS: tuple[str, ...] = (
    "senha",
    "password",
    "passwd",
    "secret",
    "token",
    "cookie",
    "credencial",
    "credential",
    "authorization",
    "auth_header",
    "cabecalho_de_autenticacao",
    "session",
    "sessao",
    "api_key",
    "apikey",
    "refresh_token",
    "client_secret",
    "html_completo",
    "ics_url",
    "ical",
)

REDACTED = "[REDACTED]"


def _is_forbidden_key(key: str) -> bool:
    low = str(key).lower()
    return any(fragment in low for fragment in FORBIDDEN_KEY_FRAGMENTS)


def sanitize(value: Any) -> Any:
    """Remove recursivamente valores associados a chaves sensiveis.

    - dict: chaves sensiveis viram REDACTED; demais sao sanitizadas em profundidade.
    - list/tuple: cada item e sanitizado.
    - outros tipos: retornados como estao.
    """
    if isinstance(value, dict):
        clean: dict[Any, Any] = {}
        for k, v in value.items():
            if _is_forbidden_key(k):
                clean[k] = REDACTED
            else:
                clean[k] = sanitize(v)
        return clean
    if isinstance(value, (list, tuple)):
        return [sanitize(item) for item in value]
    return value


def contains_secret_key(payload: dict[str, Any]) -> bool:
    """True se algum nivel do dicionario contiver uma chave sensivel."""
    for k, v in payload.items():
        if _is_forbidden_key(k):
            return True
        if isinstance(v, dict) and contains_secret_key(v):
            return True
        if isinstance(v, (list, tuple)):
            for item in v:
                if isinstance(item, dict) and contains_secret_key(item):
                    return True
    return False
