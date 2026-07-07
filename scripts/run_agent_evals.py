"""Executa avaliacoes de prontidao do Agente 19."""

from __future__ import annotations

import json

from app.evaluation.agent_readiness import run_agent_readiness_evals
from app.storage.db import init_db


def main() -> int:
    init_db()
    report = run_agent_readiness_evals()
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
