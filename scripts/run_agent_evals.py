"""Executa avaliacoes de prontidao do Agente 19."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

EVAL_DB = Path(tempfile.gettempdir()) / "agente_sei_agent_evals.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{EVAL_DB.as_posix()}")

from app.evaluation.agent_readiness import run_agent_readiness_evals
from app.storage.db import init_db


def main() -> int:
    init_db()
    report = run_agent_readiness_evals()
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
