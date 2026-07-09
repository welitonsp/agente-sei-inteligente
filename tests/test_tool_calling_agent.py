"""Testes do loop de tool-calling (model-agnostic, offline com fake)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent.tool_calling_agent import (
    ClaudeChatModel,
    ModelTurn,
    ToolCall,
    ToolCallingAgent,
)


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'agent.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return db


class _ScriptedModel:
    """Modelo fake: devolve turnos pre-programados, um por chamada."""

    def __init__(self, turns: list[ModelTurn]) -> None:
        self._turns = turns
        self.calls: list[dict] = []

    def respond(self, messages, tools, *, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._turns[len(self.calls) - 1]


# --- loop feliz --------------------------------------------------------------


def test_agente_chama_ferramenta_e_conclui(db_env):
    model = _ScriptedModel(
        [
            ModelTurn(
                text="Vou consultar os manuais.",
                tool_calls=[ToolCall("t1", "consultar_manuais", {"consulta": "minuta e assinatura"})],
                stop_reason="tool_use",
            ),
            ModelTurn(text="Resumo pronto. Revisao humana obrigatoria.", stop_reason="end_turn"),
        ]
    )
    agent = ToolCallingAgent(model)
    run = agent.run("Analise o processo e explique a minuta.", usuario_local="op")

    assert run.status == "ok"
    assert run.iteracoes == 2
    assert len(run.passos) == 1
    assert run.passos[0].tool == "consultar_manuais"
    assert run.passos[0].ok
    # O resultado da ferramenta foi devolvido ao modelo no 2o turno.
    assert model.calls[1]["messages"][-1]["role"] == "user"


def test_agente_sem_ferramenta_responde_direto(db_env):
    model = _ScriptedModel([ModelTurn(text="Nao preciso de ferramentas.", stop_reason="end_turn")])
    run = ToolCallingAgent(model).run("Oi")
    assert run.status == "ok"
    assert run.iteracoes == 1
    assert run.passos == []


# --- guard barra ferramenta e o loop segue -----------------------------------


def test_ferramenta_negada_pelo_guard_volta_como_erro(db_env):
    # O modelo pede uma ferramenta fora da allow-list; o runtime nega; o agente
    # recebe o erro e conclui mesmo assim.
    model = _ScriptedModel(
        [
            ModelTurn(
                tool_calls=[ToolCall("t1", "assinar_documento", {})],
                stop_reason="tool_use",
            ),
            ModelTurn(text="Nao posso assinar; encaminho para revisao humana.", stop_reason="end_turn"),
        ]
    )
    run = ToolCallingAgent(model).run("Assine o documento")
    assert run.status == "ok"
    assert run.passos[0].status == "negado"
    # O bloco devolvido ao modelo marca erro.
    ultimo_user = model.calls[1]["messages"][-1]["content"][0]
    assert ultimo_user["is_error"] is True


# --- orcamento de iteracoes --------------------------------------------------


def test_para_no_limite_de_iteracoes(db_env):
    laco = ModelTurn(
        tool_calls=[ToolCall("t", "consultar_manuais", {"consulta": "x"})],
        stop_reason="tool_use",
    )
    model = _ScriptedModel([laco] * 10)  # nunca para sozinho
    run = ToolCallingAgent(model, max_iteracoes=3).run("loop")
    assert run.status == "max_iteracoes"
    assert run.iteracoes == 3
    assert len(run.passos) == 3


# --- ferramentas expostas ao modelo ------------------------------------------


def test_tools_sao_passadas_no_formato_claude(db_env):
    model = _ScriptedModel([ModelTurn(text="ok", stop_reason="end_turn")])
    ToolCallingAgent(model).run("oi")
    tools = model.calls[0]["tools"]
    assert any(t["name"] == "gerar_minuta" for t in tools)
    assert all({"name", "description", "input_schema"} <= set(t) for t in tools)


# --- ClaudeChatModel parseia tool_use (cliente injetado) ---------------------


class _FakeBlockText:
    type = "text"
    text = "ola"


class _FakeBlockTool:
    type = "tool_use"
    id = "abc"
    name = "consultar_manuais"
    input = {"consulta": "y"}


class _FakeResp:
    content = [_FakeBlockText(), _FakeBlockTool()]
    stop_reason = "tool_use"


class _FakeMessages:
    def create(self, **kwargs):
        _FakeMessages.last = kwargs
        return _FakeResp()


class _FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()


def test_claude_chat_model_extrai_texto_e_tool_use():
    model = ClaudeChatModel(client=_FakeClient())
    turn = model.respond([{"role": "user", "content": "oi"}], [{"name": "consultar_manuais"}], system="s")
    assert turn.text == "ola"
    assert turn.stop_reason == "tool_use"
    assert turn.tool_calls[0].name == "consultar_manuais"
    assert turn.tool_calls[0].input == {"consulta": "y"}
