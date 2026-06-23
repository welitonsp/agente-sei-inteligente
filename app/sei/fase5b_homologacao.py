"""Avaliador de prontidao da FASE 5B.

Mesmo quando cadastro e seletores estiverem validos, este modulo nao autoriza
escrita real. Ele apenas informa se a homologacao controlada pode ser preparada.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.sei.minuta_cadastro import MinutaCadastro, validate_minuta_cadastro
from app.sei.selector_manifest import evaluate_selector_manifest


@dataclass(frozen=True)
class Phase5BReadiness:
    """Resultado de prontidao para homologacao."""

    ready_for_homologation: bool
    real_write_allowed: bool
    blockers: tuple[str, ...]


def evaluate_phase5b_readiness(
    *,
    cadastro: MinutaCadastro,
    selector_manifest: dict,
    required_fields: tuple[str, ...] = (),
) -> Phase5BReadiness:
    """Combina validacoes de cadastro e seletores."""
    cadastro_report = validate_minuta_cadastro(
        cadastro,
        required_fields=required_fields,
    )
    selector_report = evaluate_selector_manifest(selector_manifest)

    blockers = cadastro_report.violations + selector_report.blockers
    return Phase5BReadiness(
        ready_for_homologation=not blockers,
        real_write_allowed=False,
        blockers=tuple(blockers),
    )
