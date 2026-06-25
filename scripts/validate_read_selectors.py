"""Validador estritamente local (dry-run) dos seletores de LEITURA do SEI.

NAO abre navegador. NAO usa Playwright. NAO faz requests. NAO toca no SEI.
Apenas le o JSON local e valida a estrutura contra read_selector_manifest.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.sei.read_selector_manifest import evaluate_read_selector_manifest  # noqa: E402

MANIFEST_PATH = Path("knowledge_base/sei_homologacao/read_selectors.template.json")


def run() -> int:
    print("\n--- Validador de Seletores de LEITURA (FASE 5C - Frente 2) ---")
    if not MANIFEST_PATH.exists():
        print(f"Erro: arquivo {MANIFEST_PATH} nao encontrado.")
        return 1

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    report = evaluate_read_selector_manifest(manifest)
    print(f"\nVersao: {report.version}")
    print("Status:", "[OK] valido" if report.ok else "[PENDENTE] ainda nao homologado")
    if report.missing:
        print("Ausentes:", ", ".join(report.missing))
    if report.not_homologated:
        print("Nao homologados (pending):", ", ".join(report.not_homologated))
    if report.forbidden:
        print("Bloqueios de seguranca:", ", ".join(report.forbidden))

    print("\nAVISO: seletores 'pending' sao candidatos; nenhuma leitura/escrita real")
    print("e executada por este script. Homologue de forma supervisionada (logado).")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
