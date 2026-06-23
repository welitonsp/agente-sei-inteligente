"""Token de confirmacao para minuta controlada.

O token amarra processo + tipo de documento + hash do texto. Se qualquer parte
mudar, a validacao falha e a minuta nao prossegue.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


def text_hash(texto: str) -> str:
    """Hash SHA-256 do texto final revisado."""
    normalized = str(texto).replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _canonical_payload(processo_sei: str, tipo_documento: str, texto_hash: str) -> str:
    return "|".join(
        [
            str(processo_sei).strip(),
            str(tipo_documento).strip().lower(),
            str(texto_hash).strip().lower(),
        ]
    )


@dataclass(frozen=True)
class MinutaConfirmation:
    """Confirmacao humana serializavel, sem texto integral."""

    processo_sei: str
    tipo_documento: str
    text_hash: str
    token: str


def generate_minuta_token(
    *,
    processo_sei: str,
    tipo_documento: str,
    texto: str,
    secret: str,
) -> MinutaConfirmation:
    """Gera token HMAC para o texto final confirmado."""
    digest = text_hash(texto)
    payload = _canonical_payload(processo_sei, tipo_documento, digest)
    token = hmac.new(
        str(secret).encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return MinutaConfirmation(
        processo_sei=str(processo_sei).strip(),
        tipo_documento=str(tipo_documento).strip(),
        text_hash=digest,
        token=token,
    )


def verify_minuta_token(
    *,
    processo_sei: str,
    tipo_documento: str,
    texto: str,
    token: str,
    secret: str,
) -> bool:
    """Valida token sem comparar strings de forma vulneravel a timing."""
    expected = generate_minuta_token(
        processo_sei=processo_sei,
        tipo_documento=tipo_documento,
        texto=texto,
        secret=secret,
    )
    return hmac.compare_digest(expected.token, str(token))
