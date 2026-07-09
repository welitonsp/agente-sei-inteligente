# 64 — Plano de sucesso do Agente 19

Data: 2026-07-08
Status: guia ativo de execução.

Este documento é o guia oficial para levar o Agente 19 de protótipo a
**funcionário digital operacional**, sempre com custo zero, supervisão humana e o
guard como barreira final.

## Definição de sucesso

Na rotina real, com custo zero e sempre supervisionado, o agente:
**lê → resume → classifica para o 19 CRPM → sugere providência → gera minuta →
avisa prazo**, com auditoria e revisão humana obrigatória. Nenhum ato oficial
automático.

## Princípio central

O caminho crítico **não é mais código** — é transformar a knowledge base do
19 CRPM em dado real. Tudo que já existe (leitura, resumo, minuta, guarda, IA
sob Claude) só entrega valor quando a triagem conhece as regras da unidade.
Por isso o plano roda em **duas trilhas paralelas**: a sua (dados/decisões) e a
de engenharia (código de apoio), convergindo em marcos.

## Invariantes (nunca relaxar)

1. Custo zero por padrão (sem API paga, sem hospedagem paga).
2. Revisão humana obrigatória; atos oficiais no SEI são manuais.
3. Guard (`sei_action_guard`) antes de toda ação — o prompt nunca é a barreira.

## Marco 1 — MVP operacional (2–3 sprints)

### Sprint 1 — Knowledge base real (desbloqueia tudo)
- **Você:** unidades do 19 CRPM, regras de direcionamento, palavras-chave e
  5 casos anonimizados. Guia em `knowledge_base/fluxos_19crpm/COMO_PREENCHER.md`.
- **Engenharia:** montar/validar CSVs + testes de homologação.
- **Aceite:** triagem deixa de retornar `indefinido`; acerta unidade+regra em ≥4/5 casos.

### Sprint 2 — Alertas de prazo (Telegram) — *entregue como base*
- **Você:** confirmar Telegram como canal e o chat/grupo (`TELEGRAM_CHAT_ID`).
- **Engenharia:** serviço `app/integrations/telegram_service.py` (dry-run por
  padrão, real via `.env`), ligado ao extrator de prazos.
- **Aceite:** prazo detectado dispara alerta no chat configurado, sem documento integral.

### Sprint 3 — Skills com contrato JSON
- **Engenharia:** formalizar `resumidor-administrativo`, `extrator-prazos`,
  `extrator-eventos`, `auditor-processos` (docs/24), saída JSON + confiança + fontes.
- **Aceite:** cada skill retorna JSON validado e revisão humana obrigatória, com testes.

## Marco 2 — Homologação e integrações reais (paralelo)

- **Leitura real do SEI (FASE 4):** infra pronta; homologar com processo anonimizado; evidências em `docs/32`.
- **Google Agenda real:** concluir OAuth uma vez; validar um evento de teste.
- **OCR local gratuito:** implementar para PDFs escaneados (custo zero).

## Marco 3 — Minuta controlada no SEI (só com autorização)

- **FASE 5B:** contratos e manifesto prontos, `real_write_allowed=false` por
  design. Avança só com seletores homologados **e autorização institucional
  expressa**, parando antes de assinar/tramitar/enviar.

## Trilha contínua de qualidade

- Unificar os dois orquestradores (`mission_control` × grafo LangGraph) em PR próprio.
- Suíte verde + ruff limpo a cada PR.
- Documentação contínua (regra docs/29): changelog e status a cada entrega.

## Estado atual (2026-07-08)

- Núcleo de IA auditado: grafo roteado por `ai_provider` (Claude), crítico
  fail-closed, auditoria persistida (ver `docs/33` e PR da auditoria).
- Serviço de Telegram entregue em dry-run (Sprint 2 iniciado).
- Esqueleto da knowledge base pronto para preenchimento (Sprint 1 aguarda seus dados).
- Suíte: 297 testes (288 + 9 do Telegram), ruff limpo.

## Próxima ação

O gargalo é o **Sprint 1**: seus dados do 19 CRPM. Enquanto reúne, a engenharia
adianta o que não depende deles (skills, OCR). Assim que você confirmar o canal
Telegram e o chat, ativamos os alertas reais de prazo.
