"""Autenticacao local simples para o painel do Agente 19.

Esta camada identifica o usuario local e seu perfil operacional. Ela nao usa,
nao pede e nao aceita senha do SEI, cookie, token ou sessao de navegador.
"""

from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Mapping


ROLE_OPERADOR = "operador"
ROLE_REVISOR = "revisor"
ROLE_GESTOR = "gestor"

VALID_ROLES = frozenset({ROLE_OPERADOR, ROLE_REVISOR, ROLE_GESTOR})

ENDPOINT_PERMISSIONS: dict[str, frozenset[str]] = {
    "/api/import-text": frozenset({ROLE_OPERADOR, ROLE_GESTOR}),
    "/api/import-pdf": frozenset({ROLE_OPERADOR, ROLE_GESTOR}),
    "/api/generate-draft": frozenset({ROLE_OPERADOR, ROLE_REVISOR, ROLE_GESTOR}),
    "/api/triage-local": frozenset({ROLE_OPERADOR, ROLE_REVISOR, ROLE_GESTOR}),
    "/api/mission-control": frozenset({ROLE_OPERADOR, ROLE_REVISOR, ROLE_GESTOR}),
    "/api/agent19": frozenset({ROLE_OPERADOR, ROLE_REVISOR, ROLE_GESTOR}),
}

FORBIDDEN_CREDENTIAL_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-sei-password",
        "x-sei-senha",
        "x-sei-token",
        "x-agente19-password",
        "x-agente19-senha",
    }
)

FORBIDDEN_CREDENTIAL_PAYLOAD_KEYS = frozenset(
    {
        "senha",
        "senha-sei",
        "password",
        "login-sei",
        "cookie",
        "session",
        "token",
    }
)


@dataclass(frozen=True)
class AuthContext:
    usuario_local: str
    perfil: str

    def to_metadata(self) -> dict[str, str]:
        return {"usuario_local": self.usuario_local, "perfil_local": self.perfil}


class AuthError(Exception):
    def __init__(self, status: HTTPStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message

    def to_error(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code, "message": self.message}}


def authorize_dashboard_request(
    path: str,
    headers: Mapping[str, str],
    payload: Mapping[str, object] | None = None,
) -> AuthContext:
    """Autoriza um endpoint local do painel por usuario e perfil.

    O mecanismo e propositalmente simples para o MVP local. A evolucao natural
    e trocar os headers por sessao local autenticada, mantendo este contrato de
    perfil e permissao.
    """
    if path not in ENDPOINT_PERMISSIONS:
        raise AuthError(
            HTTPStatus.NOT_FOUND,
            "UNKNOWN_ENDPOINT",
            "Endpoint local desconhecido.",
        )

    normalized_headers = {_normalize_key(k): str(v) for k, v in headers.items()}
    forbidden_header = sorted(
        key for key in normalized_headers if key in FORBIDDEN_CREDENTIAL_HEADERS
    )
    if forbidden_header:
        raise AuthError(
            HTTPStatus.BAD_REQUEST,
            "FORBIDDEN_CREDENTIAL",
            "Credencial, senha, cookie ou token nao deve ser enviado ao Agente 19.",
        )

    payload_keys = {_normalize_key(key) for key in (payload or {}).keys()}
    if payload_keys & FORBIDDEN_CREDENTIAL_PAYLOAD_KEYS:
        raise AuthError(
            HTTPStatus.BAD_REQUEST,
            "FORBIDDEN_CREDENTIAL",
            "Payload nao pode conter senha, cookie, token ou credencial do SEI.",
        )

    usuario = _clean_user(_get_header(normalized_headers, "x-agente19-user"))
    perfil = _normalize_role(_get_header(normalized_headers, "x-agente19-role"))

    if not usuario:
        raise AuthError(
            HTTPStatus.UNAUTHORIZED,
            "AUTH_REQUIRED",
            "Informe o usuario local no header X-Agente19-User.",
        )
    if perfil not in VALID_ROLES:
        raise AuthError(
            HTTPStatus.FORBIDDEN,
            "INVALID_ROLE",
            "Perfil local invalido. Use operador, revisor ou gestor.",
        )
    if perfil not in ENDPOINT_PERMISSIONS[path]:
        raise AuthError(
            HTTPStatus.FORBIDDEN,
            "ROLE_NOT_ALLOWED",
            "Perfil local sem permissao para esta acao.",
        )
    return AuthContext(usuario_local=usuario, perfil=perfil)


def apply_auth_to_payload(
    payload: dict[str, object], auth: AuthContext
) -> dict[str, object]:
    """Inclui identidade local no payload sem sobrescrever usuario explicito."""
    enriched = dict(payload)
    if not str(enriched.get("usuario_local", "")).strip():
        enriched["usuario_local"] = auth.usuario_local
    enriched["perfil_local"] = auth.perfil
    return enriched


def _get_header(headers: Mapping[str, str], key: str) -> str:
    return str(headers.get(key, "")).strip()


def _normalize_key(value: object) -> str:
    return str(value).strip().lower().replace("_", "-")


def _normalize_role(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _clean_user(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    return cleaned[:80]
