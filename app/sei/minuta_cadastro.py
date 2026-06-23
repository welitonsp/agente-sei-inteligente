"""Contrato de cadastro para FASE 5B em homologacao.

Antes de qualquer escrita real, o cadastro da minuta precisa explicitar tipo de
documento ja existente, nivel de acesso e campos administrativos aplicaveis.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NivelAcesso(str, Enum):
    """Niveis de acesso esperados no cadastro do documento SEI."""

    PUBLICO = "publico"
    RESTRITO = "restrito"
    SIGILOSO = "sigiloso"


ALLOWED_REQUIRED_FIELDS = frozenset(
    {
        "descricao",
        "interessado",
        "destinatario",
        "hipotese_legal",
    }
)


@dataclass(frozen=True)
class MinutaCadastro:
    """Dados confirmados antes de tentar criar minuta no SEI."""

    processo_sei: str
    tipo_documento: str
    nivel_acesso: str
    text_hash: str
    descricao: str = ""
    interessado: str = ""
    destinatario: str = ""
    hipotese_legal: str = ""


@dataclass(frozen=True)
class CadastroValidation:
    """Resultado da validacao de cadastro."""

    ok: bool
    violations: tuple[str, ...]


def validate_minuta_cadastro(
    cadastro: MinutaCadastro,
    *,
    required_fields: tuple[str, ...] = (),
) -> CadastroValidation:
    """Valida campos obrigatorios sem acessar o SEI."""
    violations: list[str] = []

    if not cadastro.processo_sei.strip():
        violations.append("processo_sei obrigatorio.")
    if not cadastro.tipo_documento.strip():
        violations.append("tipo_documento existente no SEI obrigatorio.")
    if not cadastro.text_hash.strip():
        violations.append("text_hash obrigatorio.")

    nivel = cadastro.nivel_acesso.strip().lower()
    valid_levels = {level.value for level in NivelAcesso}
    if not nivel:
        violations.append("nivel_acesso obrigatorio.")
    elif nivel not in valid_levels:
        violations.append("nivel_acesso invalido.")

    if nivel in {NivelAcesso.RESTRITO.value, NivelAcesso.SIGILOSO.value}:
        if not cadastro.hipotese_legal.strip():
            violations.append("hipotese_legal obrigatoria para acesso restrito/sigiloso.")

    unknown_required = set(required_fields) - ALLOWED_REQUIRED_FIELDS
    if unknown_required:
        joined = ", ".join(sorted(unknown_required))
        violations.append(f"campos obrigatorios desconhecidos: {joined}.")

    for field_name in required_fields:
        value = getattr(cadastro, field_name, "")
        if not str(value).strip():
            violations.append(f"{field_name} obrigatorio para este tipo documental.")

    return CadastroValidation(ok=not violations, violations=tuple(violations))
