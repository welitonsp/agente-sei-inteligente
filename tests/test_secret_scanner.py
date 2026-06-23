from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_scanner():
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_no_secrets.py"
    spec = importlib.util.spec_from_file_location("check_no_secrets", script)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_scanner_ignora_env_example_sem_valores(tmp_path):
    scanner = _load_scanner()
    env_example = tmp_path / ".env.example"
    env_example.write_text(
        "GOOGLE_CLIENT_SECRET=\nGOOGLE_REFRESH_TOKEN=<valor_impresso>\n",
        encoding="utf-8",
    )

    assert scanner.scan_files(tmp_path, [env_example]) == []


def test_scanner_detecta_refresh_token_concreto(tmp_path):
    scanner = _load_scanner()
    leak = tmp_path / "leak.txt"
    fake_token = "1//" + ("a" * 48)
    leak.write_text(f"GOOGLE_REFRESH_TOKEN={fake_token}\n", encoding="utf-8")

    findings = scanner.scan_files(tmp_path, [leak])

    assert len(findings) == 1
    assert findings[0].rule == "secret_env_assignment"


def test_scanner_bloqueia_env_versionado(tmp_path):
    scanner = _load_scanner()
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=local\n", encoding="utf-8")

    findings = scanner.scan_files(tmp_path, [env_file])

    assert len(findings) == 1
    assert findings[0].rule == "tracked_env_file"
