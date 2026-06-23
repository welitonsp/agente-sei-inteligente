"""Testes de credenciais OAuth (sem rede)."""

from app.integrations import google_auth
from app.integrations.google_auth import SCOPES


class _Settings:
    def __init__(self, cid="", csec="", rtok=""):
        self.google_client_id = cid
        self.google_client_secret = csec
        self.google_refresh_token = rtok


def test_escopos_minimos_corretos():
    assert "https://www.googleapis.com/auth/calendar.events" in SCOPES
    assert "https://www.googleapis.com/auth/contacts.readonly" in SCOPES


def test_is_configured_falso_quando_incompleto():
    assert google_auth.is_configured(_Settings()) is False
    assert google_auth.is_configured(_Settings(cid="x", csec="y")) is False


def test_is_configured_verdadeiro_quando_completo():
    s = _Settings(cid="x", csec="y", rtok="z")
    assert google_auth.is_configured(s) is True


def test_build_credentials_none_sem_config():
    assert google_auth.build_credentials(_Settings()) is None


def test_build_credentials_constroi_objeto_offline():
    s = _Settings(cid="cid", csec="csec", rtok="rtok")
    creds = google_auth.build_credentials(s)
    assert creds is not None
    assert creds.refresh_token == "rtok"
    # Sem token de acesso ainda (renovacao ocorre na 1a chamada de API).
    assert creds.token is None
