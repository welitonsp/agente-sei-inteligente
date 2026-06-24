"""Script CLI offline para simulacao operacional ponta a ponta (FASE 5D-S).

Este script NUNCA acessa a rede, NUNCA abre navegador e NUNCA modifica o SEI.
"""

import json
from pathlib import Path

from app.sei.fase5d_simulacao import simulate_phase5d_operation
from app.sei.minuta_cadastro import MinutaCadastro

MANIFEST_PATH = Path("knowledge_base/sei_homologacao/minuta_selectors.template.json")


def run() -> None:
    print("\n========================================================")
    print(" FASE 5D-S: SIMULACAO OPERACIONAL PONTA A PONTA")
    print("========================================================")
    
    if not MANIFEST_PATH.exists():
        print(f"[ERRO] Arquivo manifesto nao encontrado: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("\n1. Criando Cadastro Simulado...")
    cadastro = MinutaCadastro(
        processo_sei="202600000123456",
        tipo_documento="Despacho",
        nivel_acesso="publico",
        text_hash="simulacao1234567890abcdef",
        descricao="Despacho Simulado Teste",
    )
    print(f"   -> Processo: {cadastro.processo_sei}")
    print(f"   -> Tipo: {cadastro.tipo_documento}")

    print("\n2. Executando Motor de Simulacao Offline...")
    report = simulate_phase5d_operation(
        cadastro=cadastro,
        selector_manifest=manifest,
    )

    print(f"\nStatus Estrutural: {'[OK] Valido' if report.ok else '[FALHOU] Bloqueado'}")

    if not report.ok:
        print("\n[ BLOCKERS ENCONTRADOS ]")
        for b in report.blockers:
            print(f" - {b}")
    else:
        print("\n[ PLANO OPERACIONAL SIMULADO (DRY-RUN) ]")
        for i, step in enumerate(report.simulated_plan, 1):
            acao = step.get("action", "")
            alvo = step.get("target", "")
            dado = step.get("data", "")
            
            detalhe = f" -> alvo: '{alvo}'"
            if dado:
                detalhe += f" | dado: '{dado}'"
                
            print(f" {i:02d}. [{acao.upper()}] {step['step']}{detalhe}")

    print("\n========================================================")
    print(" GARANTIAS DE SEGURANCA RETORNADAS PELO MOTOR:")
    print(f" - Operação real habilitada?          {'SIM' if report.real_write_allowed else 'NÃO'}")
    print(f" - Pronto para operação real?         {'SIM' if report.ready_for_real_write else 'NÃO'}")
    print(f" - Requisito para proxima fase:       {report.next_phase_required}")
    print("========================================================\n")


if __name__ == "__main__":
    run()
