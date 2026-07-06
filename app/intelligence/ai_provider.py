"""Camada de provedor de IA com papéis lógicos (Claude no controle).

Inspirada no padrão LiteLLM observado no ecossistema oficial do SEI
(anatelgovbr/sei-ia, ver docs/52): o código chama um **papel lógico**
(`RESUMO`, `CLASSIFICACAO`, `MINUTA`, `TRIAGEM`), não um modelo concreto. Isso
desacopla a aplicação do provedor — trocar de modelo/provedor é configuração,
não alteração de código.

Decisão de projeto: **Claude (Anthropic) é o provedor padrão**. O guard de
ações (`app/sei/sei_action_guard`) continua sendo a barreira final — toda
geração consulta o guard ANTES de qualquer chamada de rede; o prompt nunca é a
barreira. Para testes e operação offline/custo-zero existe o `EchoProvider`,
determinístico e sem rede.

Reliability: o SDK da Anthropic já reexecuta automaticamente 429/5xx com
backoff exponencial e NÃO reexecuta erros de autenticação — exatamente a
política desejada. Configuramos apenas `max_retries` por papel.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from app.core.config import Settings, get_settings
from app.core.permissions import Action
from app.sei.sei_action_guard import GuardRequest, evaluate

# Modelo padrão do Claude (ver skill claude-api). Nunca rebaixar sem decisão.
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"


class AIRole(str, Enum):
    """Papéis lógicos de IA, independentes do modelo concreto."""

    RESUMO = "resumo"
    CLASSIFICACAO = "classificacao"
    MINUTA = "minuta"
    TRIAGEM = "triagem"


@dataclass(frozen=True)
class RoleConfig:
    """Configuração de um papel: modelo, limites e a ação SEI correspondente."""

    model: str
    max_tokens: int
    sei_action: Action
    effort: str | None = None  # low | medium | high | max
    adaptive_thinking: bool = False
    max_retries: int = 3


# Papel -> ação do guard. Geração de minuta exige mais cuidado (effort alto +
# adaptive thinking); resumo/classificação são tarefas simples e baratas.
DEFAULT_ROLE_CONFIGS: dict[AIRole, RoleConfig] = {
    AIRole.RESUMO: RoleConfig(
        model=DEFAULT_CLAUDE_MODEL, max_tokens=1024,
        sei_action=Action.RESUMIR, effort="low",
    ),
    AIRole.CLASSIFICACAO: RoleConfig(
        model=DEFAULT_CLAUDE_MODEL, max_tokens=512,
        sei_action=Action.CLASSIFICAR, effort="low",
    ),
    AIRole.TRIAGEM: RoleConfig(
        model=DEFAULT_CLAUDE_MODEL, max_tokens=512,
        sei_action=Action.CLASSIFICAR, effort="low",
    ),
    AIRole.MINUTA: RoleConfig(
        model=DEFAULT_CLAUDE_MODEL, max_tokens=4096,
        sei_action=Action.GERAR_MINUTA, effort="high", adaptive_thinking=True,
    ),
}


@dataclass(frozen=True)
class AICompletion:
    """Resultado neutro de uma geração de IA."""

    text: str
    role: AIRole
    model: str
    stop_reason: str = ""
    usage: dict[str, Any] = field(default_factory=dict)


class AIProvider(Protocol):
    def complete(
        self, role: AIRole, prompt: str, *, system: str | None = None
    ) -> AICompletion:
        """Gera texto para o papel informado. Levanta em caso de bloqueio/erro."""
        ...

    @property
    def is_real(self) -> bool:
        """True se o provedor efetivamente chama um serviço externo (pago)."""
        ...


def _assert_role_allowed(role: AIRole, config: RoleConfig) -> None:
    """Barreira final: consulta o guard antes de qualquer chamada de IA."""
    result = evaluate(GuardRequest(acao_solicitada=config.sei_action.value))
    if not result.permitido:
        raise PermissionError(
            f"[GUARD] Papel '{role.value}' bloqueado: {result.motivo}"
        )


class EchoProvider:
    """Provedor offline e determinístico (testes / custo zero).

    Não acessa rede e não depende do SDK da Anthropic. Ainda assim respeita o
    guard, para que o comportamento de segurança seja idêntico ao real.
    """

    is_real = False

    def __init__(self, role_configs: dict[AIRole, RoleConfig] | None = None) -> None:
        self._configs = role_configs or DEFAULT_ROLE_CONFIGS

    def complete(
        self, role: AIRole, prompt: str, *, system: str | None = None
    ) -> AICompletion:
        config = self._configs[role]
        _assert_role_allowed(role, config)
        trecho = " ".join(str(prompt).split())[:200]
        return AICompletion(
            text=f"[ECHO:{role.value}] {trecho}",
            role=role,
            model="echo",
            stop_reason="end_turn",
            usage={"input_tokens": 0, "output_tokens": 0},
        )


class ClaudeProvider:
    """Provedor real baseado no SDK oficial da Anthropic (Claude).

    O SDK `anthropic` é importado de forma tardia para não ser dependência dos
    testes nem do caminho offline. Um `client` pode ser injetado (testes).
    """

    is_real = True

    def __init__(
        self,
        *,
        api_key: str = "",
        role_configs: dict[AIRole, RoleConfig] | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key
        self._configs = role_configs or DEFAULT_ROLE_CONFIGS
        self._client = client

    def _build_client(self, max_retries: int) -> Any:
        if self._client is not None:
            return self._client
        api_key = self._api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "Credencial da IA ausente. Defina ANTHROPIC_API_KEY no .env "
                "local, ou use AI_PROVIDER=echo para operar offline."
            )
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depende de extra opcional
            raise RuntimeError(
                "Provedor Claude requer o pacote 'anthropic'. "
                "Instale-o ou use AI_PROVIDER=echo."
            ) from exc
        return anthropic.Anthropic(api_key=api_key, max_retries=max_retries)

    def complete(
        self, role: AIRole, prompt: str, *, system: str | None = None
    ) -> AICompletion:
        config = self._configs[role]
        _assert_role_allowed(role, config)

        client = self._build_client(config.max_retries)

        kwargs: dict[str, Any] = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "messages": [{"role": "user", "content": str(prompt)}],
        }
        if system:
            kwargs["system"] = system
        if config.adaptive_thinking:
            kwargs["thinking"] = {"type": "adaptive"}
        if config.effort:
            kwargs["output_config"] = {"effort": config.effort}

        response = client.messages.create(**kwargs)
        text = _extract_text(response)
        return AICompletion(
            text=text,
            role=role,
            model=getattr(response, "model", config.model),
            stop_reason=getattr(response, "stop_reason", "") or "",
            usage=_usage_dict(response),
        )


def _extract_text(response: Any) -> str:
    partes = []
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text":
            partes.append(str(getattr(block, "text", "")))
    return "".join(partes).strip()


def _usage_dict(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    return {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
    }


def get_ai_provider(settings: Settings | None = None) -> AIProvider:
    """Fábrica do provedor de IA conforme `AI_PROVIDER` (padrão: claude)."""
    cfg = settings or get_settings()
    nome = (cfg.ai_provider or "claude").strip().lower()

    configs = DEFAULT_ROLE_CONFIGS
    if cfg.ai_model:
        # Override do modelo para todos os papéis, mantendo limites/effort.
        configs = {
            role: RoleConfig(
                model=cfg.ai_model,
                max_tokens=rc.max_tokens,
                sei_action=rc.sei_action,
                effort=rc.effort,
                adaptive_thinking=rc.adaptive_thinking,
                max_retries=rc.max_retries,
            )
            for role, rc in DEFAULT_ROLE_CONFIGS.items()
        }

    if nome in {"echo", "none", "memoria", "dry_run", "offline"}:
        return EchoProvider(role_configs=configs)
    if nome in {"claude", "anthropic"}:
        return ClaudeProvider(api_key=cfg.anthropic_api_key, role_configs=configs)
    raise ValueError(
        f"AI_PROVIDER invalido: '{cfg.ai_provider}'. Use 'claude' ou 'echo'."
    )
