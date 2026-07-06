"""Testes Mutacionais de Segurança para o Guardião do SEI.

Garante que nenhuma refatoração afrouxe a política Zero Trust (Default Deny)
do sistema em relação aos atos oficiais e ações não autorizadas.
"""

import pytest

from app.core.permissions import Action
from app.sei.sei_action_guard import GuardRequest, evaluate, assert_allowed, GuardDecision


def test_guard_blocks_forbidden_actions_hard():
    """Garante que atos oficiais do SEI são sumariamente bloqueados."""
    # Ação totalmente proibida de ser automatizada
    request = GuardRequest(
        acao_solicitada=Action.ASSINAR_DOCUMENTO.value,
        justificativa="O usuário pediu."
    )
    
    result = evaluate(request)
    
    # Assertivas cruciais de segurança
    assert result.permitido is False
    assert result.decisao == GuardDecision.BLOQUEADO
    assert result.acao == Action.ASSINAR_DOCUMENTO.value
    assert result.revisao_humana_obrigatoria is True
    
    # Valida comportamento defensivo que aborta a thread
    with pytest.raises(PermissionError) as exc_info:
        assert_allowed(request)
    
    assert "[GUARD] BLOQUEADO:" in str(exc_info.value)


def test_guard_blocks_unknown_actions_default_deny():
    """Garante que ações não mapeadas caem no Default Deny."""
    request = GuardRequest(acao_solicitada="AÇÃO_HACKER_INVENTADA")
    result = evaluate(request)
    
    assert result.permitido is False
    assert result.decisao == GuardDecision.BLOQUEADO
    assert result.metadata.get("regra") == "default_deny_desconhecida"


def test_guard_allows_safe_actions():
    """Garante que operações inofensivas passam livremente."""
    request = GuardRequest(acao_solicitada=Action.RESUMIR.value)
    result = evaluate(request)
    
    assert result.permitido is True
    assert result.decisao == GuardDecision.PERMITIDO
    assert result.metadata.get("regra") == "lista_positiva"


def test_guard_requires_human_approval_for_sensitive():
    """Garante que ações sensíveis (ex: Gerar Minuta) exijam humano."""
    # Cenário 1: Agente tenta sozinho (Bloqueado/Precisa Revisão)
    request_unapproved = GuardRequest(
        acao_solicitada=Action.SALVAR_MINUTA.value,
        aprovado_por_humano=False
    )
    result_unapproved = evaluate(request_unapproved)
    
    assert result_unapproved.permitido is False
    assert result_unapproved.decisao == GuardDecision.PRECISA_REVISAO
    
    # Cenário 2: Humano aperta o botão verde explicitamente (Permitido)
    request_approved = GuardRequest(
        acao_solicitada=Action.SALVAR_MINUTA.value,
        aprovado_por_humano=True
    )
    result_approved = evaluate(request_approved)
    
    assert result_approved.permitido is True
    assert result_approved.decisao == GuardDecision.PERMITIDO
