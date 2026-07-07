"""Testes da autenticacao local do painel."""

from __future__ import annotations

from http import HTTPStatus

import pytest

from app.core.auth import (
    AuthError,
    apply_auth_to_payload,
    authorize_dashboard_request,
)


def test_operador_pode_criar_missao():
    auth = authorize_dashboard_request(
        "/api/mission-control",
        {"X-Agente19-User": "operador.local", "X-Agente19-Role": "operador"},
        {"titulo": "Teste"},
    )

    assert auth.usuario_local == "operador.local"
    assert auth.perfil == "operador"


def test_operador_pode_chamar_agente19():
    auth = authorize_dashboard_request(
        "/api/agent19",
        {"X-Agente19-User": "operador.local", "X-Agente19-Role": "operador"},
        {"mensagem": "Analise"},
    )

    assert auth.usuario_local == "operador.local"
    assert auth.perfil == "operador"


def test_sem_usuario_local_e_bloqueado():
    with pytest.raises(AuthError) as exc:
        authorize_dashboard_request(
            "/api/mission-control",
            {"X-Agente19-Role": "operador"},
            {"titulo": "Teste"},
        )

    assert exc.value.status == HTTPStatus.UNAUTHORIZED
    assert exc.value.code == "AUTH_REQUIRED"


def test_perfil_invalido_e_bloqueado():
    with pytest.raises(AuthError) as exc:
        authorize_dashboard_request(
            "/api/mission-control",
            {"X-Agente19-User": "x", "X-Agente19-Role": "visitante"},
            {"titulo": "Teste"},
        )

    assert exc.value.status == HTTPStatus.FORBIDDEN
    assert exc.value.code == "INVALID_ROLE"


def test_revisor_nao_importa_texto():
    with pytest.raises(AuthError) as exc:
        authorize_dashboard_request(
            "/api/import-text",
            {"X-Agente19-User": "revisor.local", "X-Agente19-Role": "revisor"},
            {"titulo": "Teste"},
        )

    assert exc.value.status == HTTPStatus.FORBIDDEN
    assert exc.value.code == "ROLE_NOT_ALLOWED"


def test_senha_ou_token_no_payload_sao_bloqueados():
    with pytest.raises(AuthError) as exc:
        authorize_dashboard_request(
            "/api/mission-control",
            {"X-Agente19-User": "operador.local", "X-Agente19-Role": "operador"},
            {"titulo": "Teste", "senha_sei": "nao-pode"},
        )

    assert exc.value.status == HTTPStatus.BAD_REQUEST
    assert exc.value.code == "FORBIDDEN_CREDENTIAL"


def test_authorization_header_e_bloqueado():
    with pytest.raises(AuthError) as exc:
        authorize_dashboard_request(
            "/api/mission-control",
            {
                "X-Agente19-User": "operador.local",
                "X-Agente19-Role": "operador",
                "Authorization": "Bearer segredo",
            },
            {"titulo": "Teste"},
        )

    assert exc.value.status == HTTPStatus.BAD_REQUEST
    assert exc.value.code == "FORBIDDEN_CREDENTIAL"


def test_apply_auth_to_payload_preenche_usuario_local():
    auth = authorize_dashboard_request(
        "/api/mission-control",
        {"X-Agente19-User": "operador.local", "X-Agente19-Role": "operador"},
        {"titulo": "Teste"},
    )

    payload = apply_auth_to_payload({"titulo": "Teste"}, auth)

    assert payload["usuario_local"] == "operador.local"
    assert payload["perfil_local"] == "operador"
