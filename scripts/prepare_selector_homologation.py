"""Script offline para auxiliar na coleta e validacao supervisionada de seletores.

NAO abre navegador.
Opera somente offline e nao utiliza navegador, automacao web ou chamadas de rede.
Apenas le o manifesto local, valida estruturalmente e exibe no terminal.
"""

import json
from pathlib import Path

from app.sei.selector_manifest import evaluate_selector_manifest

MANIFEST_PATH = Path("knowledge_base/sei_homologacao/minuta_selectors.template.json")


def run() -> None:
    print("\n========================================================")
    print(" FASE 5C-H: RELATORIO DE HOMOLOGACAO DE SELETORES")
    print("========================================================")
    
    if not MANIFEST_PATH.exists():
        print(f"[ERRO] Arquivo nao encontrado: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    report = evaluate_selector_manifest(manifest)
    selectors = manifest.get("selectors", {})

    print(f"\nVersao do Manifesto: {report.version}")
    print(f"Status Estrutural: {'[OK] Pronto' if report.ok else '[FALHOU] Nao homologado'}")

    print("\n--- DETALHAMENTO DOS SELETORES ---")
    
    # Todos os seletores presentes no JSON
    for key, info in selectors.items():
        status = info.get("status", "pending")
        value = info.get("value", "")
        if status == "validated":
            print(f"[ VALIDADO ] {key} -> '{value}'")
        else:
            print(f"[ PENDENTE ] {key} -> '{value}'")

    print("\n--- AVALIACAO E BLOQUEIOS ---")
    if report.missing:
        print(f"(-) Ausentes (Obrigatorios): {', '.join(report.missing)}")
    else:
        print("(+) Nenhum seletor obrigatorio ausente.")

    if report.not_homologated:
        print(f"(-) Nao homologados (Pendentes): {', '.join(report.not_homologated)}")
    else:
        print("(+) Todos os seletores minimos estao validados.")

    if report.forbidden:
        print(f"(-) Termos Proibidos Encontrados: {', '.join(report.forbidden)}")
    else:
        print("(+) Nenhum bloqueio de seguranca por termos proibidos.")

    print("\n========================================================")
    print(" AVISO DE SEGURANCA:")
    print(" - Este script e apenas um validador estrutural e local.")
    print(" - A marcacao 'validated' NAO autoriza escrita real no SEI.")
    print(" - A FASE 5B (Criacao de Minutas Real) continua sendo FUTURA.")
    print("========================================================\n")


if __name__ == "__main__":
    run()
