"""Testes do diagnostico seguro de API SEI/WSSEI."""

from __future__ import annotations

import urllib.error
import urllib.request

import pytest

from app.core.config import Settings
from app.sei.api_discovery import (
    build_api_candidates,
    classify_status,
    discover_public_api,
)


def test_build_api_candidates_monta_wssei_e_wsdl():
    candidates = build_api_candidates("https://sei.go.gov.br/sei/")
    urls = {candidate.name: candidate.url for candidate in candidates}

    assert urls["mod-wssei-v2"] == (
        "https://sei.go.gov.br/sei/modulos/wssei/controlador_ws.php/api/v2"
    )
    assert urls["mod-wssei-v1"] == (
        "https://sei.go.gov.br/sei/modulos/wssei/controlador_ws.php/api/v1"
    )
    assert urls["sei-soap-wsdl"] == "https://sei.go.gov.br/sei/ws/SeiWS.php?wsdl"


def test_build_api_candidates_recusa_url_com_credencial():
    with pytest.raises(ValueError):
        build_api_candidates("https://usuario:senha@sei.go.gov.br/sei/")


def test_build_api_candidates_exige_https():
    with pytest.raises(ValueError):
        build_api_candidates("http://sei.go.gov.br/sei/")


def test_classify_status_nao_autoriza_uso_real():
    assert classify_status(200)[0] == "possivelmente_disponivel"
    assert classify_status(401)[0] == "existe_mas_bloqueado"
    assert classify_status(403)[0] == "existe_mas_bloqueado"
    assert classify_status(404)[0] == "nao_encontrado"
    assert classify_status(500)[0] == "erro_servidor"


def test_discovery_nao_envia_cookie_authorization_ou_payload():
    seen: list[urllib.request.Request] = []

    def fake_opener(request: urllib.request.Request, timeout: float) -> int:
        seen.append(request)
        return 401

    results = discover_public_api(
        Settings(sei_base_url="https://sei.go.gov.br/sei/"),
        opener=fake_opener,
    )

    assert len(results) == 3
    assert {result.classification for result in results} == {"existe_mas_bloqueado"}
    assert seen
    for request in seen:
        headers = {key.lower(): value for key, value in request.header_items()}
        assert "cookie" not in headers
        assert "authorization" not in headers
        assert request.data is None


def test_discovery_classifica_http_error_sem_expor_credencial():
    def fake_opener(request: urllib.request.Request, timeout: float) -> int:
        raise urllib.error.HTTPError(
            request.full_url,
            404,
            "not found",
            hdrs=None,
            fp=None,
        )

    results = discover_public_api(
        Settings(sei_base_url="https://sei.go.gov.br/sei/"),
        opener=fake_opener,
    )

    assert {result.classification for result in results} == {"nao_encontrado"}


def test_discovery_trata_conexao_interrompida_como_indisponivel():
    def fake_opener(request: urllib.request.Request, timeout: float) -> int:
        raise ConnectionResetError("conexao encerrada pelo host remoto")

    results = discover_public_api(
        Settings(sei_base_url="https://sei.go.gov.br/sei/"),
        opener=fake_opener,
    )

    assert {result.classification for result in results} == {"indisponivel"}
