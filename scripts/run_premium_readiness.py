"""Executa o gate premium de prontidao do Agente 19."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

EVAL_DB = Path(tempfile.gettempdir()) / "agente_sei_premium_readiness.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{EVAL_DB.as_posix()}")

from app.evaluation.agent_readiness import run_agent_readiness_evals  # noqa: E402
from app.evaluation.premium_readiness import run_premium_readiness  # noqa: E402
from app.storage.db import init_db  # noqa: E402


def main() -> int:
    init_db()
    agent_report = run_agent_readiness_evals()
    report = run_premium_readiness(ROOT_DIR, agent_report)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
