"""Diagnostico seguro de disponibilidade de API SEI/WSSEI.

Esta rotina nao autentica, nao envia usuario/senha, nao envia cookies, nao le
sessao e nao tenta chamar operacoes de negocio. Ela apenas verifica URLs
publicas provaveis para orientar decisao humana.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

from app.core.config import Settings, get_settings


DEFAULT_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class ApiCandidate:
    """Endpoint candidato a API publica/sem autenticacao."""

    name: str
    url: str
    kind: str


@dataclass(frozen=True)
class ApiProbeResult:
    """Resultado sanitizado de uma tentativa sem credenciais."""

    name: str
    url: str
    kind: str
    http_status: int | None
    classification: str
    detail: str


def build_api_candidates(sei_base_url: str) -> tuple[ApiCandidate, ...]:
    """Monta URLs candidatas a partir da URL oficial do SEI."""
    base = _validate_sei_base_url(sei_base_url)
    return (
        ApiCandidate(
            name="mod-wssei-v2",
            kind="rest",
            url=urllib.parse.urljoin(
                base,
                "modulos/wssei/controlador_ws.php/api/v2",
            ),
        ),
        ApiCandidate(
            name="mod-wssei-v1",
            kind="rest",
            url=urllib.parse.urljoin(
                base,
                "modulos/wssei/controlador_ws.php/api/v1",
            ),
        ),
        ApiCandidate(
            name="sei-soap-wsdl",
            kind="soap_wsdl",
            url=urllib.parse.urljoin(base, "ws/SeiWS.php?wsdl"),
        ),
    )


def discover_public_api(
    settings: Settings | None = None,
    *,
    opener: Callable[[urllib.request.Request, float], int] | None = None,
) -> tuple[ApiProbeResult, ...]:
    """Executa diagnostico sem credenciais nas URLs candidatas."""
    cfg = settings or get_settings()
    candidates = build_api_candidates(cfg.sei_base_url)
    probe = opener or _default_probe
    return tuple(_probe_candidate(candidate, probe) for candidate in candidates)


def _probe_candidate(
    candidate: ApiCandidate,
    opener: Callable[[urllib.request.Request, float], int],
) -> ApiProbeResult:
    request = urllib.request.Request(
        candidate.url,
        method="GET",
        headers={
            "Accept": "application/json, text/xml;q=0.8, */*;q=0.1",
            "User-Agent": "Agente19-ApiDiscovery/1.0",
        },
    )
    try:
        status = opener(request, DEFAULT_TIMEOUT_SECONDS)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
    except (urllib.error.URLError, OSError):
        return ApiProbeResult(
            name=candidate.name,
            url=candidate.url,
            kind=candidate.kind,
            http_status=None,
            classification="indisponivel",
            detail="Falha de rede ou DNS ao consultar endpoint candidato.",
        )
    except TimeoutError:
        return ApiProbeResult(
            name=candidate.name,
            url=candidate.url,
            kind=candidate.kind,
            http_status=None,
            classification="timeout",
            detail="Tempo limite excedido ao consultar endpoint candidato.",
        )

    classification, detail = classify_status(status)
    return ApiProbeResult(
        name=candidate.name,
        url=candidate.url,
        kind=candidate.kind,
        http_status=status,
        classification=classification,
        detail=detail,
    )


def classify_status(status: int) -> tuple[str, str]:
    """Classifica status HTTP sem inferir acesso autorizado."""
    if status in {200, 204}:
        return (
            "possivelmente_disponivel",
            "Endpoint respondeu sem autenticacao; uso real ainda exige autorizacao.",
        )
    if status in {401, 403}:
        return (
            "existe_mas_bloqueado",
            "Endpoint parece existir, mas exige autenticacao/autorizacao.",
        )
    if status == 404:
        return ("nao_encontrado", "Endpoint candidato nao encontrado.")
    if 300 <= status < 400:
        return (
            "redireciona",
            "Endpoint redirecionou; confirmar manualmente sem expor credenciais.",
        )
    if 500 <= status < 600:
        return ("erro_servidor", "Servidor respondeu com erro.")
    return ("inconclusivo", f"Status HTTP {status} nao conclusivo.")


def _default_probe(request: urllib.request.Request, timeout: float) -> int:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return int(response.status)


def _validate_sei_base_url(sei_base_url: str) -> str:
    parsed = urllib.parse.urlparse(str(sei_base_url).strip())
    if parsed.scheme != "https":
        raise ValueError("Diagnostico de API SEI exige URL HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("URL do SEI nao pode conter credenciais.")
    if not parsed.netloc:
        raise ValueError("URL do SEI invalida.")
    path = parsed.path or "/sei/"
    if not path.endswith("/"):
        path = f"{path}/"
    return urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, path, "", "", "")
    )
