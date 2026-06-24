"""Testes da camada de provedor de IA (Claude no controle)."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.intelligence.ai_provider import (
    DEFAULT_CLAUDE_MODEL,
    AICompletion,
    AIRole,
    ClaudeProvider,
    EchoProvider,
    get_ai_provider,
)


# --- Fakes para testar o ClaudeProvider sem rede nem SDK ---------------------

class _FakeBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _FakeUsage:
    input_tokens = 10
    output_tokens = 5


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.content = [_FakeBlock(text)]
        self.model = DEFAULT_CLAUDE_MODEL
        self.stop_reason = "end_turn"
        self.usage = _FakeUsage()


class _FakeMessages:
    def __init__(self) -> None:
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeResponse("minuta gerada pelo Claude")


class _FakeClient:
    def __init__(self) -> None:
        self.messages = _FakeMessages()


# --- EchoProvider ------------------------------------------------------------

def test_echo_provider_offline_e_determinista():
    p = EchoProvider()
    assert p.is_real is False
    r = p.complete(AIRole.RESUMO, "Texto de teste para resumir.")
    assert isinstance(r, AICompletion)
    assert r.model == "echo"
    assert r.text.startswith("[ECHO:resumo]")
    # Determinístico
    assert p.complete(AIRole.RESUMO, "Texto de teste para resumir.").text == r.text


# --- ClaudeProvider (cliente injetado) ---------------------------------------

def test_claude_provider_monta_request_de_minuta():
    fake = _FakeClient()
    p = ClaudeProvider(client=fake)
    r = p.complete(AIRole.MINUTA, "Gerar despacho.", system="Você é um assessor.")

    assert p.is_real is True
    assert r.text == "minuta gerada pelo Claude"
    assert r.model == DEFAULT_CLAUDE_MODEL
    assert r.usage == {"input_tokens": 10, "output_tokens": 5}

    kw = fake.messages.last_kwargs
    assert kw["model"] == DEFAULT_CLAUDE_MODEL
    assert kw["max_tokens"] == 4096
    assert kw["system"] == "Você é um assessor."
    # Minuta usa adaptive thinking + effort alto (tarefa complexa).
    assert kw["thinking"] == {"type": "adaptive"}
    assert kw["output_config"] == {"effort": "high"}


def test_claude_provider_resumo_e_simples_sem_thinking():
    fake = _FakeClient()
    ClaudeProvider(client=fake).complete(AIRole.RESUMO, "resumir isto")
    kw = fake.messages.last_kwargs
    assert kw["max_tokens"] == 1024
    assert "thinking" not in kw  # resumo é simples: sem thinking
    assert kw["output_config"] == {"effort": "low"}


def test_claude_provider_sem_credencial_falha_claro():
    p = ClaudeProvider(api_key="")  # sem client injetado, sem env
    import os

    antigo = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        with pytest.raises(RuntimeError, match="Credencial da IA ausente"):
            p.complete(AIRole.RESUMO, "x")
    finally:
        if antigo is not None:
            os.environ["ANTHROPIC_API_KEY"] = antigo


# --- Fábrica -----------------------------------------------------------------

def test_factory_padrao_e_claude():
    p = get_ai_provider(Settings(ai_provider=""))
    assert isinstance(p, ClaudeProvider)
    assert p.is_real is True


def test_factory_echo_offline():
    p = get_ai_provider(Settings(ai_provider="echo"))
    assert isinstance(p, EchoProvider)


def test_factory_override_de_modelo():
    p = get_ai_provider(Settings(ai_provider="echo", ai_model="claude-sonnet-4-6"))
    assert p._configs[AIRole.MINUTA].model == "claude-sonnet-4-6"


def test_factory_provider_invalido():
    with pytest.raises(ValueError, match="AI_PROVIDER invalido"):
        get_ai_provider(Settings(ai_provider="gpt-9"))
