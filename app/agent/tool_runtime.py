"""Runtime de ferramentas guardado do Agente 19 — equivalente seguro ao
"AI Agent node" do n8n.

Motivacao (docs/52, achado 5 sobre `SEI-Pro/mcp-seipro`): expor muitas
ferramentas a um agente aumenta o risco de **agencia excessiva**. Nossa
diferenca em relacao a n8n/MCP genericos e que **toda invocacao de ferramenta
passa pela allow-list + `sei_action_guard` + auditoria**, com default-deny e zero
ferramentas perigosas. O LLM (ou um planner deterministico) escolhe a ferramenta;
o guard, que e codigo e nao prompt, decide se ela pode rodar.

Cada ferramenta (um "node") declara:
- `input_schema` no formato de tool-use do Claude (pronto para o loop de LLM);
- a `Action` de permissao que o guard avalia ANTES de executar;
- um handler que embrulha uma capacidade ja existente e segura.

Nenhuma ferramenta aqui assina, envia, tramita, conclui, da ciencia, exclui ou
usa credencial — essas acoes sao proibidas de forma dura em `permissions.py`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from app.core import audit
from app.core.permissions import Action
from app.sei.sei_action_guard import GuardRequest, evaluate

_logger = logging.getLogger("agente19.tool_runtime")

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ExecutableTool:
    nome: str
    descricao: str
    acao: Action  # avaliada pelo guard antes de executar
    input_schema: dict[str, Any]
    handler: ToolHandler
    read_only: bool = True

    def to_llm_tool(self) -> dict[str, Any]:
        """Formato de tool-use do Claude (name/description/input_schema)."""
        return {
            "name": self.nome,
            "description": self.descricao,
            "input_schema": self.input_schema,
        }


@dataclass(frozen=True)
class ToolResult:
    tool: str
    status: str  # ok | negado | erro
    output: dict[str, Any] = field(default_factory=dict)
    motivo: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


# --------------------------------------------------------------------------- #
# Handlers: cada um embrulha uma capacidade local ja testada e segura.
# --------------------------------------------------------------------------- #


def _h_consultar_manuais(args: dict[str, Any]) -> dict[str, Any]:
    from app.intelligence.manual_retriever import retrieve_context

    consulta = str(args.get("consulta", ""))
    k = int(args.get("k", 4) or 4)
    return {"contexto": retrieve_context(consulta, k=k)}


def _h_analisar_processo(args: dict[str, Any]) -> dict[str, Any]:
    from app.intelligence.institutional_analyzer import analyze_document_rules

    return analyze_document_rules(str(args.get("texto", "")))


def _h_triagem_19crpm(args: dict[str, Any]) -> dict[str, Any]:
    from app.intelligence.local_triage import TriageRequest, analyze_triage

    return analyze_triage(
        TriageRequest(
            assunto=str(args.get("assunto", "")),
            texto=str(args.get("texto", "")),
            processo_sei=str(args.get("processo_sei", "")),
            usuario_local=str(args.get("usuario_local", "")),
            origem="tool_runtime",
        )
    ).to_contract()


def _h_gerar_minuta(args: dict[str, Any]) -> dict[str, Any]:
    from app.intelligence.local_minutador import DraftRequest, generate_draft

    return generate_draft(
        DraftRequest(
            assunto=str(args.get("assunto", "")),
            resumo=str(args.get("resumo", "")),
            texto_base=str(args.get("texto_base", "")),
            processo_sei=str(args.get("processo_sei", "")),
            tipo_minuta=str(args.get("tipo_minuta", "")),
            unidade_destino=str(args.get("unidade_destino", "")),
            providencia=str(args.get("providencia", "")),
            prazo=str(args.get("prazo", "")),
            usuario_local=str(args.get("usuario_local", "")),
            origem="tool_runtime",
        )
    ).to_contract()


def _h_avaliar_redacao(args: dict[str, Any]) -> dict[str, Any]:
    from app.intelligence.redacao_goias_policy import evaluate_redacao

    return evaluate_redacao(
        str(args.get("texto", "")),
        tipo_minuta=str(args.get("tipo_minuta", "")),
    ).to_contract()


def _texto_schema(**extra: dict[str, Any]) -> dict[str, Any]:
    props: dict[str, Any] = {"texto": {"type": "string", "description": "Texto do processo/documento."}}
    props.update(extra)
    return {"type": "object", "properties": props, "required": ["texto"]}


def build_default_registry() -> dict[str, ExecutableTool]:
    """Allow-list das ferramentas seguras do Agente 19 (default-deny fora daqui)."""
    tools = [
        ExecutableTool(
            nome="consultar_manuais",
            descricao=(
                "Consulta as regras curadas dos manuais (SEI e Redacao de Goias) "
                "relevantes para a consulta. Retorna trechos com a fonte citada."
            ),
            acao=Action.LER_DOCUMENTO,
            input_schema={
                "type": "object",
                "properties": {
                    "consulta": {"type": "string", "description": "Assunto/pergunta."},
                    "k": {"type": "integer", "description": "Numero de trechos (padrao 4)."},
                },
                "required": ["consulta"],
            },
            handler=_h_consultar_manuais,
        ),
        ExecutableTool(
            nome="analisar_processo",
            descricao="Analisa o texto do processo e retorna tipo, resumo, prazos e providencia.",
            acao=Action.RESUMIR,
            input_schema=_texto_schema(),
            handler=_h_analisar_processo,
        ),
        ExecutableTool(
            nome="triagem_19crpm",
            descricao="Classifica o interesse do 19 CRPM e sugere unidade destino por regras locais.",
            acao=Action.CLASSIFICAR,
            input_schema=_texto_schema(
                assunto={"type": "string"},
                processo_sei={"type": "string"},
                usuario_local={"type": "string"},
            ),
            handler=_h_triagem_19crpm,
        ),
        ExecutableTool(
            nome="gerar_minuta",
            descricao="Gera uma minuta administrativa local (rascunho externo) para revisao humana.",
            acao=Action.GERAR_MINUTA,
            input_schema={
                "type": "object",
                "properties": {
                    "assunto": {"type": "string"},
                    "resumo": {"type": "string"},
                    "texto_base": {"type": "string"},
                    "processo_sei": {"type": "string"},
                    "tipo_minuta": {"type": "string"},
                    "unidade_destino": {"type": "string"},
                    "providencia": {"type": "string"},
                    "prazo": {"type": "string"},
                    "usuario_local": {"type": "string"},
                },
                "required": ["assunto"],
            },
            handler=_h_gerar_minuta,
            read_only=False,
        ),
        ExecutableTool(
            nome="avaliar_redacao",
            descricao="Avalia a minuta contra o Manual de Redacao de Goias (checklist, bloqueios).",
            acao=Action.CLASSIFICAR,
            input_schema=_texto_schema(tipo_minuta={"type": "string"}),
            handler=_h_avaliar_redacao,
        ),
    ]
    return {tool.nome: tool for tool in tools}


class ToolRuntime:
    """Executor de ferramentas com allow-list + guard + auditoria por chamada."""

    def __init__(self, registry: dict[str, ExecutableTool] | None = None) -> None:
        self._registry = registry if registry is not None else build_default_registry()

    def list_for_llm(self) -> list[dict[str, Any]]:
        """Catalogo no formato de tool-use do Claude (para o loop de agente)."""
        return [tool.to_llm_tool() for tool in self._registry.values()]

    def tool_names(self) -> list[str]:
        return list(self._registry)

    def invoke(
        self,
        name: str,
        args: dict[str, Any] | None = None,
        *,
        usuario_local: str = "",
        processo_sei: str = "",
        aprovado_por_humano: bool = False,
    ) -> ToolResult:
        """Invoca uma ferramenta com barreira deterministica antes de executar."""
        args = dict(args or {})

        # 1) Allow-list (default-deny): ferramenta desconhecida nunca roda.
        tool = self._registry.get(name)
        if tool is None:
            self._audit(name, "negado", usuario_local, processo_sei,
                        "Ferramenta fora da allow-list do Agente 19.")
            return ToolResult(tool=name, status="negado",
                              motivo="Ferramenta fora da allow-list do Agente 19.")

        # 2) Guard: avalia a acao ANTES de executar (barreira e codigo, nao prompt).
        guard_req = GuardRequest(
            acao_solicitada=tool.acao.value,
            origem="tool_runtime",
            usuario_local=usuario_local,
            processo_sei=processo_sei or str(args.get("processo_sei", "")),
            justificativa=f"Invocacao da ferramenta '{name}' pelo Agente 19.",
            aprovado_por_humano=aprovado_por_humano,
        )
        guard_res = evaluate(guard_req)
        try:
            audit.record_guard_decision(guard_req, guard_res)
        except Exception as exc:  # auditoria e secundaria a decisao
            _logger.warning("Falha ao auditar guard de '%s': %s", name, exc)
        if not guard_res.permitido:
            return ToolResult(tool=name, status="negado", motivo=guard_res.motivo)

        # 3) Executa o handler seguro.
        try:
            output = tool.handler(args)
        except Exception as exc:
            _logger.warning("Ferramenta '%s' falhou: %s", name, exc)
            self._audit(name, "erro", usuario_local, processo_sei, str(exc))
            return ToolResult(tool=name, status="erro", motivo=str(exc))

        self._audit(name, "ok", usuario_local, processo_sei,
                    f"Ferramenta '{name}' executada.")
        return ToolResult(tool=name, status="ok", output=output)

    @staticmethod
    def _audit(name: str, result: str, usuario_local: str, processo_sei: str, reason: str) -> None:
        try:
            audit.record(
                action="TOOL_INVOKE",
                result=result,
                actor_id=usuario_local or None,
                target_type="ferramenta_agente",
                target_id=name,
                reason=reason,
                metadata={"processo_sei": processo_sei or None, "texto_integral_persistido": False},
            )
        except Exception as exc:  # nunca deixar a auditoria derrubar o fluxo
            _logger.warning("Falha ao auditar invocacao de '%s': %s", name, exc)


@dataclass(frozen=True)
class PlanStep:
    """Um passo de um plano de ferramentas (analogo a um node de workflow n8n)."""

    tool: str
    args: dict[str, Any] = field(default_factory=dict)


def run_plan(
    steps: list[PlanStep],
    *,
    runtime: ToolRuntime | None = None,
    usuario_local: str = "",
    processo_sei: str = "",
) -> list[ToolResult]:
    """Executa um plano de ferramentas em sequencia, cada passo sob o guard.

    Nao interrompe em passo negado/erro: coleta todos os resultados para que o
    orquestrador (ou o LLM) veja o que passou e o que foi barrado. A decisao
    final permanece humana e cada passo fica auditado.
    """
    runtime = runtime or ToolRuntime()
    return [
        runtime.invoke(
            step.tool,
            step.args,
            usuario_local=usuario_local,
            processo_sei=processo_sei,
        )
        for step in steps
    ]


__all__ = [
    "ExecutableTool",
    "PlanStep",
    "ToolResult",
    "ToolRuntime",
    "build_default_registry",
    "run_plan",
]
