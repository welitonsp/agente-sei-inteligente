"""Validador estritamente local (dry-run) de seletores do SEI.

Este script NAO abre navegador.
Este script NAO usa Playwright.
Este script NAO faz requests HTTP.
Este script NAO interage com o SEI real.

Sua unica funcao e ler o arquivo JSON local e validar sua estrutura
contra as regras definidas em app.sei.selector_manifest.
"""

import json
from pathlib import Path
from app.sei.selector_manifest import evaluate_selector_manifest

MANIFEST_PATH = Path("knowledge_base/sei_homologacao/minuta_selectors.template.json")


def run() -> None:
    print("\n--- Validador Estatico de Manifesto de Seletores (FASE 5B-H) ---")
    
    if not MANIFEST_PATH.exists():
        print(f"Erro: Arquivo {MANIFEST_PATH} nao encontrado.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    report = evaluate_selector_manifest(manifest)

    print(f"\nVersao do manifesto: {report.version}")
    
    if report.ok:
        print("Status: [OK] Estruturalmente valido para homologacao.")
    else:
        print("Status: [FALHOU] Manifesto invalido para homologacao.")
        
    if report.missing:
        print(f"Seletores ausentes: {', '.join(report.missing)}")
    if report.not_homologated:
        print(f"Seletores nao homologados (pending/ausente): {', '.join(report.not_homologated)}")
    if report.forbidden:
        print(f"Bloqueios de seguranca (termos proibidos): {', '.join(report.forbidden)}")

    print("\nAVISO DE SEGURANCA:")
    print("- Seletores 'pending' sao apenas candidatos e nao estao homologados.")
    print("- Nenhuma escrita real esta habilitada.")
    print("- A FASE 5B real continua sendo futura.")


if __name__ == "__main__":
    run()
