"""Simulacao operacional da FASE 5D-S (Sem escrita real).

Este modulo executa o planejamento de uma operacao de criacao de minuta
sem abrir navegador, sem acionar automacao web e sem chamadas de rede.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.sei.fase5b_homologacao import evaluate_phase5b_readiness
from app.sei.minuta_cadastro import MinutaCadastro


@dataclass(frozen=True)
class Phase5DSimulationReport:
    """Relatorio de simulacao operacional."""

    ok: bool
    blockers: tuple[str, ...]
    simulated_plan: tuple[dict[str, str], ...]
    real_write_allowed: bool = False
    ready_for_real_write: bool = False
    next_phase_required: str = "nova auditoria e autorização expressa"


def simulate_phase5d_operation(
    *,
    cadastro: MinutaCadastro,
    selector_manifest: dict[str, Any],
) -> Phase5DSimulationReport:
    """Gera um plano de execucao simulado se a homologacao estiver valida.
    
    Nunca abre navegador. Nunca acessa a rede. Nunca executa automacao real.
    """
    # Usar a validacao existente da Fase 5B
    readiness = evaluate_phase5b_readiness(
        cadastro=cadastro,
        selector_manifest=selector_manifest,
        required_fields=(),
    )

    if not readiness.ready_for_homologation:
        return Phase5DSimulationReport(
            ok=False,
            blockers=readiness.blockers,
            simulated_plan=(),
        )

    # Gerar plano simulado
    selectors = selector_manifest.get("selectors", {})
    plan = (
        {
            "step": "Verificar processo aberto",
            "action": "simulated_validation_step",
            "target": selectors.get("process_number_area", {}).get("value", ""),
        },
        {
            "step": "Verificar botão de inclusão",
            "action": "simulated_selector_check",
            "target": selectors.get("include_document_button", {}).get("value", ""),
        },
        {
            "step": "Mapear pesquisa de tipo",
            "action": "simulated_field_mapping",
            "target": selectors.get("document_type_search", {}).get("value", ""),
            "data": cadastro.tipo_documento,
        },
        {
            "step": "Verificar opção de tipo",
            "action": "simulated_selector_check",
            "target": selectors.get("document_type_option", {}).get("value", ""),
        },
        {
            "step": "Mapear descrição",
            "action": "simulated_field_mapping",
            "target": selectors.get("document_description", {}).get("value", ""),
            "data": cadastro.descricao or "",
        },
        {
            "step": "Mapear nivel de acesso",
            "action": "simulated_field_mapping",
            "target": selectors.get("document_access_level", {}).get("value", ""),
            "data": cadastro.nivel_acesso,
        },
        {
            "step": "Verificar frame do editor",
            "action": "simulated_validation_step",
            "target": selectors.get("editor_frame", {}).get("value", ""),
        },
        {
            "step": "Mapear payload da minuta",
            "action": "simulated_editor_payload",
            "target": selectors.get("editor_body", {}).get("value", ""),
            "data": "<conteudo da minuta omitido>",
        },
        {
            "step": "Verificar seletor de salvamento bloqueado",
            "action": "simulated_save_blocked",
            "target": selectors.get("save_button", {}).get("value", ""),
        },
    )

    return Phase5DSimulationReport(
        ok=True,
        blockers=(),
        simulated_plan=plan,
    )
