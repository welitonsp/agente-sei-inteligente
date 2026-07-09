"""Loop de tool-calling do Agente 19 — o "cérebro" que escolhe ferramentas.

Completa a visao do agente tipo n8n: um modelo recebe uma missao e decide, em
loop, quais ferramentas chamar ate concluir. Nossa diferenca de seguranca
permanece: **cada invocacao passa pelo `ToolRuntime`**, ou seja, pela allow-list
+ `sei_action_guard` + auditoria. O modelo sugere; o guard, que e codigo, decide.

O LLM fica atras de um adaptador (`ChatModel`), entao o loop e model-agnostic e
100% testavel offline com um fake. `ClaudeChatModel` implementa o adaptador com
tool-use nativo do Claude; `build_default_agent()` monta o agente real.

Regra-mae inalterada: o agente prepara/sugere; atos oficiais no SEI sao manuais.
Nenhuma ferramenta assina, envia, tramita, conclui ou da ciencia.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.agent.tool_runtime import ToolResult, ToolRuntime
from app.intelligence.ai_provider import DEFAULT_CLAUDE_MODEL

DEFAULT_SYSTEM = (
    "Voce e o Agente 19, servidor digital supervisionado do 19 CRPM. Use as "
    "ferramentas disponiveis para analisar o processo, consultar os manuais, "
    "triar o interesse do 19 CRPM, gerar minuta e avaliar a redacao. "
    "Voce NUNCA assina, envia, tramita, conclui ou da ciencia — atos oficiais "
    "sao do humano. Sempre conclua indicando que a revisao humana e obrigatoria. "
    "Se uma ferramenta for negada pelo guard, respeite a negativa e explique."
)


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    input: dict[str, Any]


@dataclass(frozen=True)
class ModelTurn:
    """Resposta de um turno do modelo."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"


class ChatModel(Protocol):
    def respond(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        system: str,
    ) -> ModelTurn:
        """Devolve o proximo turno do modelo dado o historico e as ferramentas."""
        ...


@dataclass(frozen=True)
class AgentRun:
    status: str  # ok | max_iteracoes
    resposta_final: str
    passos: list[ToolResult]
    iteracoes: int
    revisao_humana_obrigatoria: bool = True

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resposta_final": self.resposta_final,
            "ferramentas_usadas": [
                {"tool": p.tool, "status": p.status} for p in self.passos
            ],
            "iteracoes": self.iteracoes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
        }


class ToolCallingAgent:
    """Executa o loop percepcao -> escolha de ferramenta -> observacao."""

    def __init__(
        self,
        model: ChatModel,
        runtime: ToolRuntime | None = None,
        *,
        system: str = DEFAULT_SYSTEM,
        max_iteracoes: int = 6,
    ) -> None:
        self._model = model
        self._runtime = runtime or ToolRuntime()
        self._system = system
        self._max = max_iteracoes
        self._tools = self._runtime.list_for_llm()

    def run(
        self,
        objetivo: str,
        *,
        usuario_local: str = "",
        processo_sei: str = "",
    ) -> AgentRun:
        messages: list[dict[str, Any]] = [{"role": "user", "content": objetivo}]
        passos: list[ToolResult] = []

        for iteracao in range(1, self._max + 1):
            turn = self._model.respond(messages, self._tools, system=self._system)

            if turn.stop_reason != "tool_use" or not turn.tool_calls:
                return AgentRun(
                    status="ok",
                    resposta_final=turn.text,
                    passos=passos,
                    iteracoes=iteracao,
                )

            # Registra o turno do assistente (texto + pedidos de ferramenta).
            messages.append({"role": "assistant", "content": _assistant_blocks(turn)})

            # Executa cada ferramenta pedida — SEMPRE via runtime (guard + audit).
            tool_results: list[dict[str, Any]] = []
            for tc in turn.tool_calls:
                result = self._runtime.invoke(
                    tc.name,
                    tc.input,
                    usuario_local=usuario_local,
                    processo_sei=processo_sei,
                )
                passos.append(result)
                tool_results.append(_tool_result_block(tc.id, result))

            messages.append({"role": "user", "content": tool_results})

        # Excedeu o orcamento de iteracoes: para com seguranca.
        return AgentRun(
            status="max_iteracoes",
            resposta_final=(
                "Limite de iteracoes atingido. Resultados parciais preparados; "
                "revisao humana obrigatoria."
            ),
            passos=passos,
            iteracoes=self._max,
        )


def _assistant_blocks(turn: ModelTurn) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    if turn.text:
        blocks.append({"type": "text", "text": turn.text})
    for tc in turn.tool_calls:
        blocks.append(
            {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input}
        )
    return blocks


def _tool_result_block(tool_use_id: str, result: ToolResult) -> dict[str, Any]:
    if result.ok:
        content = json.dumps(result.output, ensure_ascii=False)[:4000]
        return {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": f"[{result.status}] {result.motivo}",
        "is_error": True,
    }


class ClaudeChatModel:
    """Adaptador de tool-use nativo do Claude (SDK importado de forma tardia)."""

    def __init__(
        self,
        *,
        api_key: str = "",
        model: str = DEFAULT_CLAUDE_MODEL,
        max_tokens: int = 2048,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._client = client

    def _build_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self._api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "Credencial da IA ausente. Defina ANTHROPIC_API_KEY no .env local."
            )
        import anthropic  # type: ignore[import-not-found]

        return anthropic.Anthropic(api_key=api_key)

    def respond(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        system: str,
    ) -> ModelTurn:
        client = self._build_client()
        response = client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        for block in getattr(response, "content", []) or []:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(str(getattr(block, "text", "")))
            elif btype == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=str(getattr(block, "id", "")),
                        name=str(getattr(block, "name", "")),
                        input=dict(getattr(block, "input", {}) or {}),
                    )
                )
        return ModelTurn(
            text="".join(text_parts).strip(),
            tool_calls=tool_calls,
            stop_reason=getattr(response, "stop_reason", "end_turn") or "end_turn",
        )


def build_default_agent(*, api_key: str = "") -> ToolCallingAgent:
    """Monta o agente real (Claude + runtime de ferramentas guardado)."""
    return ToolCallingAgent(ClaudeChatModel(api_key=api_key))


__all__ = [
    "AgentRun",
    "ChatModel",
    "ClaudeChatModel",
    "ModelTurn",
    "ToolCall",
    "ToolCallingAgent",
    "build_default_agent",
]
