"""Validacoes de ambiente para impedir ativacao insegura da FASE 5.

Estas regras rodam no startup dos frontends locais. Elas nao liberam atos
oficiais; apenas bloqueiam configuracoes perigosas antes de o agente iniciar.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings


DEFAULT_MINUTA_TOKEN_SECRET = "dev-insecure-trocar-em-producao"
MIN_MINUTA_SECRET_LENGTH = 32
PRODUCTION_ENVS = {"prod", "production"}


@dataclass(frozen=True)
class SafetyReport:
    """Resultado auditavel das validacoes de ambiente."""

    ok: bool
    violations: tuple[str, ...]


def _is_production(app_env: str) -> bool:
    return str(app_env).strip().lower() in PRODUCTION_ENVS


def evaluate_safety(settings: Settings | None = None) -> SafetyReport:
    """Avalia travas que nao dependem de I/O.

    O foco do PATCH 4 e impedir que a simulacao da FASE 5A seja confundida com
    escrita real pronta em producao.
    """
    cfg = settings or get_settings()
    violations: list[str] = []

    if _is_production(cfg.app_env):
        if cfg.minuta_token_secret == DEFAULT_MINUTA_TOKEN_SECRET:
            violations.append("MINUTA_TOKEN_SECRET padrao em producao.")
        if len(cfg.minuta_token_secret.strip()) < MIN_MINUTA_SECRET_LENGTH:
            violations.append("MINUTA_TOKEN_SECRET curto em producao.")
        if cfg.enable_minuta_creation:
            violations.append(
                "ENABLE_MINUTA_CREATION ligado em producao sem FASE 5B homologada."
            )
        if cfg.log_full_text:
            violations.append("LOG_FULL_TEXT ligado em producao.")

    return SafetyReport(ok=not violations, violations=tuple(violations))


def assert_safe_environment(settings: Settings | None = None) -> SafetyReport:
    """Falha o startup quando houver configuracao proibida."""
    report = evaluate_safety(settings)
    if not report.ok:
        joined = "; ".join(report.violations)
        raise RuntimeError(f"Ambiente inseguro para iniciar o Agente 19: {joined}")
    return report
