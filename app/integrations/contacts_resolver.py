"""Resolucao dos e-mails dos Oficiais a partir do Google Contatos (People API).

O marcador "OFICIAIS" do Google Contatos contem os contatos individuais. Este
modulo localiza esse marcador (contact group/label), obtem os membros e extrai
os e-mails individuais para uso como convidados do Google Calendar.

Regras de privacidade (regra 7): nunca logar a lista de e-mails; apenas a
quantidade. Por isso o resolver NAO emite logs com e-mails; quem audita deve
registrar somente a contagem.
"""

from __future__ import annotations

from typing import Any, Protocol


def _clean_emails(emails: list[str]) -> list[str]:
    """Normaliza, remove vazios e duplicados preservando a ordem."""
    vistos: set[str] = set()
    saida: list[str] = []
    for raw in emails:
        e = (raw or "").strip().lower()
        if e and e not in vistos:
            vistos.add(e)
            saida.append(e)
    return saida


class OfficersResolver(Protocol):
    def resolve_emails(self) -> list[str]:
        """Devolve a lista de e-mails dos Oficiais (pode ser vazia)."""
        ...


class StaticOfficersResolver:
    """Resolver fixo: usado em testes e em dry-run com lista conhecida."""

    def __init__(self, emails: list[str]) -> None:
        self._emails = _clean_emails(emails)

    def resolve_emails(self) -> list[str]:
        return list(self._emails)


class GroupEmailResolver:
    """Resolver para o modo group_email: um unico e-mail de grupo."""

    def __init__(self, group_email: str) -> None:
        self._emails = _clean_emails([group_email])

    def resolve_emails(self) -> list[str]:
        return list(self._emails)


class GoogleContactsResolver:
    """Resolver real via People API a partir do nome de um marcador/label.

    As bibliotecas Google sao importadas de forma tardia para nao virarem
    dependencia obrigatoria do nucleo nem dos testes.
    """

    def __init__(self, credentials: Any, label: str) -> None:
        self._credentials = credentials
        self._label = label

    def _service(self) -> Any:
        try:
            from googleapiclient.discovery import build  # type: ignore
        except ImportError as exc:  # pragma: no cover - extra opcional
            raise RuntimeError(
                "Resolucao de contatos requer 'google-api-python-client'. "
                "Instale os extras de Google antes de usar GoogleContactsResolver."
            ) from exc
        return build("people", "v1", credentials=self._credentials)

    def _find_group_resource(self, service: Any) -> str | None:  # pragma: no cover
        """Localiza o resourceName do marcador cujo nome casa com o label."""
        alvo = self._label.strip().lower()
        page_token: str | None = None
        while True:
            resp = (
                service.contactGroups()
                .list(pageSize=200, pageToken=page_token)
                .execute()
            )
            for grupo in resp.get("contactGroups", []):
                nomes = {
                    str(grupo.get("name", "")).strip().lower(),
                    str(grupo.get("formattedName", "")).strip().lower(),
                }
                if alvo in nomes:
                    return grupo.get("resourceName")
            page_token = resp.get("nextPageToken")
            if not page_token:
                return None

    def _member_resource_names(self, service: Any, group_rn: str) -> list[str]:  # pragma: no cover
        detalhe = (
            service.contactGroups()
            .get(resourceName=group_rn, maxMembers=1000)
            .execute()
        )
        return list(detalhe.get("memberResourceNames", []))

    def _emails_from_members(self, service: Any, members: list[str]) -> list[str]:  # pragma: no cover
        emails: list[str] = []
        # getBatchGet aceita ate 200 resourceNames por chamada.
        for inicio in range(0, len(members), 200):
            lote = members[inicio : inicio + 200]
            resp = (
                service.people()
                .getBatchGet(resourceNames=lote, personFields="emailAddresses")
                .execute()
            )
            for item in resp.get("responses", []):
                pessoa = item.get("person", {})
                for endereco in pessoa.get("emailAddresses", []):
                    valor = endereco.get("value")
                    if valor:
                        emails.append(valor)
        return emails

    def resolve_emails(self) -> list[str]:  # pragma: no cover - requer rede/credenciais
        service = self._service()
        group_rn = self._find_group_resource(service)
        if not group_rn:
            return []
        members = self._member_resource_names(service, group_rn)
        if not members:
            return []
        return _clean_emails(self._emails_from_members(service, members))


def build_resolver(
    *,
    officers_source: str,
    officers_contact_label: str,
    officers_group_email: str,
    credentials: Any | None = None,
    static_emails: list[str] | None = None,
) -> OfficersResolver | None:
    """Fabrica o resolver adequado conforme a configuracao.

    - static_emails: se fornecido, sempre vence (dry-run / testes).
    - google_contacts: exige credenciais; sem elas devolve None (dry-run).
    - group_email: usa o e-mail unico.
    """
    if static_emails is not None:
        return StaticOfficersResolver(static_emails)

    if officers_source == "group_email":
        return GroupEmailResolver(officers_group_email)

    if officers_source == "google_contacts":
        if credentials is None:
            return None  # sem credenciais OAuth ainda: mantem dry-run
        return GoogleContactsResolver(credentials, officers_contact_label)

    return None
