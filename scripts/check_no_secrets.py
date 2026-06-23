"""Fail if tracked project files appear to contain concrete secrets.

This is a lightweight CI guard for the project rules in docs/28. It scans files
known to Git plus new non-ignored files, so a local ignored `.env` can exist
without being read while new files still get checked before commit. In CI, the
checkout contains the committed tree, which is the surface we need to protect.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SECRET_ENV_NAMES = (
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_CALENDAR_ICS_URL",
    "TELEGRAM_BOT_TOKEN",
    "EMAIL_PASSWORD",
    "AI_API_KEY",
    "GEMINI_API_KEY",
)

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "secret_env_assignment",
        re.compile(
            rf"\b({'|'.join(SECRET_ENV_NAMES)})\s*=\s*['\"]?([^#\s'\"]+)['\"]?"
        ),
    ),
    (
        "google_oauth_client_secret",
        re.compile(r"\bGOCSPX-[0-9A-Za-z_-]{20,}\b"),
    ),
    (
        "google_api_key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    ),
    (
        "private_key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "json_refresh_token",
        re.compile(r"(?i)\brefresh_token\b['\"]?\s*[:=]\s*['\"]([^'\"]{20,})['\"]"),
    ),
    (
        "json_client_secret",
        re.compile(r"(?i)\bclient_secret\b['\"]?\s*[:=]\s*['\"]([^'\"]{12,})['\"]"),
    ),
)

PLACEHOLDER_FRAGMENTS = (
    "<",
    ">",
    "{",
    "}",
    "...",
    "xxx",
    "changeme",
    "placeholder",
    "exemplo",
    "example",
    "valor",
    "your_",
    "settings.",
    "creds.",
    "os.environ",
)

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "data",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    snippet: str


def _looks_placeholder(value: str) -> bool:
    clean = value.strip().strip("'\"").lower()
    if not clean:
        return True
    return any(fragment in clean for fragment in PLACEHOLDER_FRAGMENTS)


def _candidate_files(root: Path) -> list[Path]:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return _walk_files(root)

    files: list[Path] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        files.append(root / line.strip())
    return files


def _walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return files


def _is_tracked_env_file(path: Path) -> bool:
    name = path.name.lower()
    return name == ".env" or (name.startswith(".env.") and name != ".env.example")


def _line_findings(path: Path, line_number: int, line: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(line):
            value = match.group(match.lastindex or 0)
            if _looks_placeholder(value):
                continue
            findings.append(
                Finding(
                    path=path,
                    line=line_number,
                    rule=rule,
                    snippet=line.strip()[:160],
                )
            )
    return findings


def scan_files(root: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.exists() or path.is_dir():
            continue
        rel = path.relative_to(root)
        if _is_tracked_env_file(rel):
            findings.append(
                Finding(
                    path=rel,
                    line=1,
                    rule="tracked_env_file",
                    snippet="Arquivo .env nao deve ser versionado.",
                )
            )
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_line_findings(rel, line_number, line))
    return findings


def scan_repo(root: Path) -> list[Finding]:
    return scan_files(root, _candidate_files(root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    findings = scan_repo(root)
    if findings:
        print("ERRO: possiveis segredos encontrados em arquivos do Git:")
        for item in findings:
            print(f"- {item.path}:{item.line} [{item.rule}] {item.snippet}")
        return 1

    print("OK: nenhum segredo concreto encontrado nos arquivos do Git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
