"""Testes do Control Plane de missoes supervisionadas."""

from __future__ import annotations

import pytest

from app.agent.control_plane import (
    build_action_proposal,
    build_supervised_mission,
    evaluate_action_proposal,
    list_tool_policies,
)


def test_tool_registry_declara_escopo_e_bloqueia_escrita_sei():
    tools = list_tool_policies()

    assert tools[0]["name"] == "mission_control"
    assert all(tool["writes_sei"] is False for tool in tools)
    assert any(tool["name"] == "calendar_agent" for tool in tools)
    assert any(tool["requires_human_approval"] for tool in tools)


def test_ferramenta_desconhecida_e_negada_por_padrao():
    with pytest.raises(PermissionError):
        build_action_proposal(
            mission_id="mis19-teste",
            tool_name="sei_clicker",
            action="ASSINAR_DOCUMENTO",
            title="Acao proibida",
            rationale="Nao deve existir ferramenta livre para clicar no SEI.",
        )


def test_ato_oficial_fica_bloqueado_no_control_plane():
    proposal = build_action_proposal(
        mission_id="mis19-teste",
        tool_name="mission_control",
        action="ASSINAR_DOCUMENTO",
        title="Assinar documento",
        rationale="Tentativa proibida de praticar ato oficial.",
    )
    decision = evaluate_action_proposal(proposal).to_contract()

    assert proposal.to_contract()["risk_level"] == "forbidden"
    assert decision["decision"] == "bloqueado"
    assert decision["guard"]["permitido"] is False


def test_acao_externa_exige_aprovacao_humana_explicita():
    proposal = build_action_proposal(
        mission_id="mis19-agenda",
        tool_name="calendar_agent",
        action="CRIAR_EVENTO_AGENDA",
        title="Criar evento de prazo",
        rationale="Preparar evento de agenda com prazo conferido pelo usuario.",
    )

    sem_aprovacao = evaluate_action_proposal(proposal).to_contract()
    com_aprovacao = evaluate_action_proposal(
        proposal, approved_by_human=True, usuario_local="operador.local"
    ).to_contract()

    assert sem_aprovacao["decision"] == "precisa_revisao"
    assert com_aprovacao["decision"] == "approved"


def test_metadados_sensiveis_sao_sanitizados():
    proposal = build_action_proposal(
        mission_id="mis19-sanitizacao",
        tool_name="mission_control",
        action="GERAR_MINUTA",
        title="Gerar rascunho",
        rationale="Gerar somente rascunho local.",
        metadata={"texto_integral": "conteudo sigiloso", "token": "abc", "ok": True},
    )
    contract = proposal.to_contract()

    assert contract["metadata"]["texto_integral"] == "[REDACTED]"
    assert contract["metadata"]["token"] == "[REDACTED]"
    assert contract["metadata"]["ok"] is True


def test_missao_supervisionada_cria_aprovacao_para_efeito_externo():
    proposal = build_action_proposal(
        mission_id="mis19-agenda",
        tool_name="calendar_agent",
        action="CRIAR_EVENTO_AGENDA",
        title="Criar evento",
        rationale="Criar evento apos aprovacao humana.",
    )
    decision = evaluate_action_proposal(proposal)
    mission = build_supervised_mission(
        mission_id="mis19-agenda",
        title="Prazo de resposta",
        proposals=[proposal],
        decisions=[decision],
        ready=True,
    ).to_contract()

    assert mission["status"] == "ready_for_review"
    assert mission["approval_requests"][0]["required"] is True
    assert mission["steps"][-1]["owner_agent"] == "human_operator"
