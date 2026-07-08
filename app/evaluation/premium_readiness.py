"""Gate de prontidao premium do Agente 19.

Este modulo transforma principios de engenharia de alto nivel em verificacoes
objetivas: seguranca por padrao, CI bloqueante, avaliacoes do agente, extensao
read-only, rastreabilidade e base de conhecimento versionada.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.permissions import FORBIDDEN_ACTIONS, is_allowed
from app.core.safety import evaluate_safety
from app.evaluation.agent_readiness import AgentEvalReport


@dataclass(frozen=True)
class PremiumCheck:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(frozen=True)
class PremiumReadinessReport:
    score: int
    passed: bool
    checks: tuple[PremiumCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
        }


def run_premium_readiness(
    root: Path,
    agent_report: AgentEvalReport | None = None,
) -> PremiumReadinessReport:
    """Executa o scorecard premium com falha dura abaixo de 100/100."""
    checks = (
        _check_safe_defaults(),
        _check_forbidden_actions(),
        _check_agent_evals(agent_report),
        _check_ci_pipeline(root),
        _check_browser_extension_read_only(root),
        _check_knowledge_base(root),
        _check_observability(root),
        _check_secure_env_example(root),
    )
    passed_count = sum(1 for check in checks if check.passed)
    score = round((passed_count / len(checks)) * 100)
    return PremiumReadinessReport(
        score=score,
        passed=all(check.passed for check in checks),
        checks=checks,
    )


def _check_safe_defaults() -> PremiumCheck:
    report = evaluate_safety()
    return PremiumCheck(
        name="safe_defaults",
        passed=report.ok,
        detail="ambiente seguro por padrao" if report.ok else "; ".join(report.violations),
    )


def _check_forbidden_actions() -> PremiumCheck:
    wrongly_allowed = sorted(action.value for action in FORBIDDEN_ACTIONS if is_allowed(action))
    return PremiumCheck(
        name="forbidden_actions_default_deny",
        passed=not wrongly_allowed,
        detail=(
            "atos oficiais bloqueados por default-deny"
            if not wrongly_allowed
            else "acoes proibidas permitidas: " + ", ".join(wrongly_allowed)
        ),
    )


def _check_agent_evals(agent_report: AgentEvalReport | None) -> PremiumCheck:
    if agent_report is None:
        return PremiumCheck(
            name="agent_readiness_evals",
            passed=False,
            detail="relatorio de avaliacoes do agente nao informado",
        )
    return PremiumCheck(
        name="agent_readiness_evals",
        passed=agent_report.passed,
        detail=f"{agent_report.passed_count}/{agent_report.total} avaliacoes passaram",
    )


def _check_ci_pipeline(root: Path) -> PremiumCheck:
    workflow = root / ".github" / "workflows" / "ci.yml"
    content = _read_text(workflow)
    required = (
        "python scripts/check_no_secrets.py .",
        "python -m pytest",
        "python scripts/run_agent_evals.py",
        "python scripts/run_premium_readiness.py",
    )
    missing = [item for item in required if item not in content]
    return PremiumCheck(
        name="ci_quality_gates",
        passed=not missing,
        detail="CI bloqueia segredos, testes, evals e readiness premium"
        if not missing
        else "faltando na CI: " + ", ".join(missing),
    )


def _check_browser_extension_read_only(root: Path) -> PremiumCheck:
    manifest = _read_text(root / "browser_extension" / "manifest.json")
    content_js = _read_text(root / "browser_extension" / "content.js")
    forbidden_snippets = (
        "<all_urls>",
        "sessionStorage",
        "." + "submit(",
        "." + "click(",
        "document.cookie",
        "localStorage",
    )
    found = [snippet for snippet in forbidden_snippets if snippet in manifest or snippet in content_js]
    has_read_only_status = "Somente leitura" in content_js and "Revisao humana" in content_js
    passed = not found and has_read_only_status
    detail = "extensao limitada ao SEI, sem RPA de escrita e com aviso de revisao humana"
    if found:
        detail = "padroes proibidos na extensao: " + ", ".join(found)
    elif not has_read_only_status:
        detail = "status de somente leitura/revisao humana ausente"
    return PremiumCheck(
        name="browser_extension_read_only",
        passed=passed,
        detail=detail,
    )


def _check_knowledge_base(root: Path) -> PremiumCheck:
    required = (
        root / "knowledge_base" / "fluxos_19crpm" / "regras_direcionamento.csv",
        root / "knowledge_base" / "fluxos_19crpm" / "palavras_chave_19crpm.csv",
        root / "knowledge_base" / "sei_github" / "fontes_github_sei.csv",
        root / "docs" / "64-pesquisa-avancada-github-sei.md",
    )
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return PremiumCheck(
        name="knowledge_base_versioned",
        passed=not missing,
        detail="base SEI/19 CRPM versionada e rastreavel"
        if not missing
        else "arquivos ausentes: " + ", ".join(missing),
    )


def _check_observability(root: Path) -> PremiumCheck:
    required = (
        root / "app" / "agent" / "tracing.py",
        root / "app" / "core" / "audit.py",
        root / "docs" / "62-tracing-ferramentas-agente19.md",
    )
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return PremiumCheck(
        name="observability_and_audit",
        passed=not missing,
        detail="tracing, auditoria e documentacao operacional presentes"
        if not missing
        else "artefatos ausentes: " + ", ".join(missing),
    )


def _check_secure_env_example(root: Path) -> PremiumCheck:
    env_example = _read_text(root / ".env.example")
    required = (
        "ALLOW_OFFICIAL_SEI_ACTIONS=false",
        "SEI_STORE_PASSWORDS=false",
        "ENABLE_SEI_BROWSER_AUTOMATION=false",
        "LOG_FULL_TEXT=false",
    )
    missing = [item for item in required if item not in env_example]
    return PremiumCheck(
        name="secure_env_example",
        passed=not missing,
        detail="env example mantem travas seguras por padrao"
        if not missing
        else "travas ausentes: " + ", ".join(missing),
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""
