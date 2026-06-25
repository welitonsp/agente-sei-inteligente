# Ícone flutuante + chat do Agente 19 (FASE 38 — Frente 1)

Primeira frente da visão operacional: depois que você loga **manualmente** no
SEI, um **ícone flutuante** fica na sua tela; ao clicar, abre um **chat** com o
Agente 19. Você manda o número do processo e cola o conteúdo; o agente analisa,
resume, acha prazos, sugere o tipo de documento, gera um rascunho e prepara um
resumo para WhatsApp/Telegram. **O agente nunca assina, envia ou tramita.**

## Como rodar
```
python -m app.desktop.floating_agent
```
- Aparece o ícone **🤖 19** (canto inferior direito; arraste para onde quiser).
- **Clique** no ícone → abre o chat. **Botão direito** no ícone → fecha.

## Fluxo do chat
1. Você: `202600000123456` + cole o texto do documento.
2. Agente responde com: **tipo provável**, **resumo**, **prazo** (com data-limite),
   **providência sugerida**, **rascunho** do documento e um **resumo para
   Telegram/WhatsApp**.
3. Você copia o rascunho para o SEI, revisa e **assina/tramita você mesmo**.

## Arquitetura
- `app/desktop/agent_chat.py` — **cérebro** do chat (lógica pura, testável):
  `AgentChatController` + `telegram_summary`. Usa o motor local (análise +
  `prazo_extractor` + minutador). Sem rede e sem GUI.
- `app/desktop/floating_agent.py` — **janela** Tkinter fina (ícone + chat).
  Tkinter é importado de forma tardia (não quebra ambiente headless).

## Limites (por design)
- O agente **não** clica no SEI nem preenche formulários nesta frente.
- **Não** assina, envia, tramita, conclui nem dá ciência (bloqueio do guard).
- Hoje você **cola** o conteúdo. A leitura automática do processo pela sua sessão
  logada é a **Frente 2** (gated por `ENABLE_SEI_BROWSER_AUTOMATION`).
- Criar o documento direto no processo é a **Frente 3 / FASE 5B**, que exige
  homologação de seletores e **autorização expressa**.

Ver também: [docs/54](54-guia-rapido-operacao.md) (guia rápido) e
[docs/38-agente-sei-rpa-assistido.md](38-agente-sei-rpa-assistido.md) (visão FASE 38).
