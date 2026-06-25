"""Homologação SUPERVISIONADA da leitura do SEI (FASE 5C — Frente 2).

Abre uma sessão de navegador EFÊMERA e SOMENTE LEITURA na URL oficial do SEI.
Você faz o login manualmente e abre um processo; o script então relata o que o
`ReadOnlyPage` consegue ler (título, URL, números de processo visíveis, itens da
árvore de documentos). Serve para confirmar que o caminho de leitura funciona no
SEI real, sem nunca clicar, preencher ou escrever.

Pré-requisitos (no SEI real, na sua máquina):
- `ENABLE_SEI_BROWSER_AUTOMATION=true` no .env local (padrão é false).
- Playwright instalado (`pip install playwright` e `playwright install chromium`).

Este script NUNCA assina, envia, tramita ou escreve. Se a flag estiver desligada,
ele se recusa a abrir o navegador.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import Settings, get_settings  # noqa: E402


def run(settings: Settings | None = None) -> str:
    cfg = settings or get_settings()
    print("\n--- Homologacao de LEITURA do SEI (read-only, supervisionada) ---")

    if not cfg.enable_sei_browser_automation:
        print("BLOQUEADO: ENABLE_SEI_BROWSER_AUTOMATION=false (padrao seguro).")
        print("Para homologar, ligue a flag no .env local e rode novamente.")
        return "bloqueado"

    # Import tardio: só quando a flag permite e o usuário roda de fato.
    from app.sei.playwright_session import open_ephemeral_readonly_session

    print("Abrindo navegador efemero na URL oficial do SEI...")
    print("1) Faca login manualmente.  2) Abra um processo.  3) Volte aqui e tecle ENTER.")
    with open_ephemeral_readonly_session(cfg) as page:
        try:
            input("Pressione ENTER apos abrir o processo no SEI... ")
        except EOFError:
            pass
        snap = page.snapshot()
        numeros = page.visible_process_numbers()
        arvore = page.document_tree()
        print("\n[LEITURA REALIZADA - SOMENTE LEITURA]")
        print("Titulo da pagina:", snap.title)
        print("URL atual:", snap.url)
        print("Numeros de processo visiveis (pagina de cima):", ", ".join(numeros[:8]) or "nenhum")
        print(f"Links na pagina de cima: {len(arvore)}")

        print("\n[FRAMES DETECTADOS - diagnostico read-only]")
        print("(o SEI monta o processo em iframes; a arvore/conteudo ficam aqui)")
        frames = page.frames_overview()
        if not frames:
            print("  Nenhum frame detectado nesta pagina.")
        for fr in frames:
            print(f"- frame name='{fr['name']}' links={fr['num_links']}")
            print(f"    url: {fr['url'][:90]}")
            for texto in fr["amostra"]:
                print(f"    . {texto}")
    print("\nSessao encerrada. Nenhuma escrita foi realizada.")
    print("Confirme os seletores reais no read_selectors.template.json e marque-os 'validated'.")
    return "ok"


if __name__ == "__main__":
    raise SystemExit(0 if run() == "ok" else 1)
