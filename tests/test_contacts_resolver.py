"""Testes da resolucao de Oficiais a partir do Google Contatos."""

from app.integrations.contacts_resolver import (
    GroupEmailResolver,
    StaticOfficersResolver,
    _clean_emails,
    build_resolver,
)


def test_clean_emails_normaliza_e_dedup():
    entrada = ["A@x.com", "a@x.com ", "", "  ", "b@X.com"]
    assert _clean_emails(entrada) == ["a@x.com", "b@x.com"]


def test_static_resolver():
    r = StaticOfficersResolver(["of1@x.com", "of1@x.com", "of2@x.com"])
    assert r.resolve_emails() == ["of1@x.com", "of2@x.com"]


def test_group_email_resolver():
    r = GroupEmailResolver("grupo@x.com")
    assert r.resolve_emails() == ["grupo@x.com"]


def test_build_resolver_prioriza_static():
    r = build_resolver(
        officers_source="google_contacts",
        officers_contact_label="OFICIAIS",
        officers_group_email="",
        static_emails=["a@x.com"],
    )
    assert r.resolve_emails() == ["a@x.com"]


def test_build_resolver_group_email():
    r = build_resolver(
        officers_source="group_email",
        officers_contact_label="OFICIAIS",
        officers_group_email="grupo@x.com",
    )
    assert r.resolve_emails() == ["grupo@x.com"]


def test_build_resolver_google_contacts_sem_credenciais_e_dry_run():
    # Regra 8: sem credenciais OAuth, mantem dry-run (resolver None).
    r = build_resolver(
        officers_source="google_contacts",
        officers_contact_label="OFICIAIS",
        officers_group_email="",
        credentials=None,
    )
    assert r is None
