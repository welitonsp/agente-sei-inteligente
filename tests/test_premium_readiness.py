from __future__ import annotations

from dataclasses import dataclass

from app.evaluation.premium_readiness import run_premium_readiness


@dataclass(frozen=True)
class _AgentReport:
    passed: bool = True
    passed_count: int = 4
    total: int = 4


def test_premium_readiness_scorecard_passa_no_repositorio_atual():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    report = run_premium_readiness(root, _AgentReport())

    assert report.passed is True
    assert report.score == 100
    assert {check.name for check in report.checks} >= {
        "safe_defaults",
        "forbidden_actions_default_deny",
        "agent_readiness_evals",
        "ci_quality_gates",
        "browser_extension_read_only",
        "knowledge_base_versioned",
        "observability_and_audit",
        "secure_env_example",
    }


def test_premium_readiness_falha_sem_relatorio_das_avaliacoes():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    report = run_premium_readiness(root, None)

    assert report.passed is False
    assert report.score < 100
    assert any(
        check.name == "agent_readiness_evals" and not check.passed
        for check in report.checks
    )
