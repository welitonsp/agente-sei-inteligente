# Agente SEI Inteligente Particular (Agente 19) — Funcionário Digital de IA do 19º CRPM

Documentacao-base do projeto do Agente 19, o Funcionario Digital de IA criado para apoiar a rotina do 19º CRPM com e-mail institucional, PDF, Google Agenda, alertas em celular, minutas administrativas e uso assistido do SEI.

Versao documental: 0.5.0
Data: 2026-07-08
Status: arquitetura particular/local supervisionada, com Control Plane de Missoes Supervisionadas, Tool Registry, ActionProposal, guard central, aprovacao humana e auditoria sanitizada. Escrita real no SEI continua nao habilitada.

## Enquadramento

O Agente SEI Inteligente Particular, tambem chamado Agente 19, e uma solucao local/particular para apoiar o usuario enquanto ele trabalha no SEI Goias com sua propria conta.

Nao ha autorizacao de API oficial, WSSEI, modulo oficial SEI IA ou acesso de TI. Por isso, o projeto nao deve se apresentar como integracao institucional oficial. O usuario faz login manualmente no SEI, diretamente na pagina oficial, e o agente apenas apoia leitura, classificacao, resumo, providencias e minutas sob supervisao humana.

**Regra-mae**: O Agente 19 prepara, sugere, organiza, cria minuta e aprende. O humano revisa, assina e pratica o ato oficial.

O sistema nao substitui a autoridade humana.

**Limites obrigatorios**: O Agente 19 NAO pode:

- pedir senha do SEI;
- armazenar senha;
- armazenar cookie;
- armazenar sessao;
- capturar token;
- assinar documento;
- tramitar processo;
- concluir processo;
- excluir documento;
- cancelar documento;
- dar ciencia automatica;
- enviar processo automaticamente;
- liberar acesso externo;
- praticar ato oficial final.

## Control Plane de Missoes Supervisionadas

A evolucao arquitetural passa a tratar cada demanda como uma **missao supervisionada**. O LLM nao decide e executa livremente: ele gera propostas estruturadas, e o Control Plane valida tudo antes de qualquer ferramenta.

Fluxo padrao:

```text
Usuario
  -> Agente 19
  -> Mission Control
  -> Agentes especializados
  -> ActionProposal
  -> Guard Central
  -> ApprovalRequest quando necessario
  -> pacote de revisao humana
```

Modelos centrais implementados em `app/agent/control_plane.py`:

- `Mission`;
- `MissionStep`;
- `AgentRun`;
- `ToolCall`;
- `ActionProposal`;
- `ApprovalRequest`;
- `AuditEvent`;
- `DecisionRecord`.

Status canonicos de missao:

```text
draft
running
needs_human_input
ready_for_review
approved
executed
blocked
failed
cancelled
```

O contrato de missao agora pode carregar `mission_id`, pacote do `control_plane`, propostas de acao, decisoes do guard, pedidos de aprovacao humana e eventos de auditoria sanitizada.

## Tool Registry

Ferramentas permitidas sao declaradas com escopo, risco e efeito externo.

Exemplo de campos do registro:

```text
name
risk_level
read_only
requires_human_approval
writes_external_system
writes_sei
allowed_actions
```

Regras:

1. ferramenta desconhecida e negada por padrao;
2. acao fora do escopo da ferramenta e bloqueada;
3. ato oficial do SEI e bloqueio duro;
4. efeito externo, como agenda ou alerta, exige aprovacao humana explicita;
5. nenhuma ferramenta registrada pode escrever no SEI.

## Modelo de sessao SEI

1. O usuario abre o SEI Goias e faz login manualmente.
2. O agente nao guarda senha.
3. O agente nao captura cookie, token ou sessao.
4. O agente nao le `localStorage`, `sessionStorage` ou headers de autenticacao.
5. A sessao Playwright, quando usada, deve ser efemera.
6. O perfil do navegador nao deve ser persistido.
7. O LLM nao controla o navegador.
8. O LLM apenas analisa texto, classifica, sugere providencia e gera conteudo.
9. Qualquer interacao com a tela do SEI deve ser feita por codigo deterministico, auditado, com allow-list e default-deny.

## Status tecnico

Conforme o enquadramento arquitetural aprovado:

1. Allow-list/default-deny implementado como regra de seguranca.
2. Chokepoint de leitura implementado como ponto unico para leitura supervisionada.
3. `app/sei/read_only_page.py` (`ReadOnlyPage`) implementado para impedir que a camada de leitura execute escrita.
4. Sessao Playwright efemera preparada.
5. Safety real implementado para bloquear credenciais, sessoes e atos oficiais.
6. FASE 5A - Minuta Controlada simulada implementada (`app/sei/minuta_writer.py`, `app/sei/minuta_token.py`, `app/sei/minuta_cadastro.py`).
7. `ENABLE_MINUTA_CREATION=false` por padrao.
8. Escrita real no SEI ainda NAO habilitada.
9. Control Plane de Missoes Supervisionadas implementado para ActionProposal, ApprovalRequest, DecisionRecord e auditoria sanitizada.

PATCH 4 permanece valido: o startup valida ambiente seguro, a escrita real permanece bloqueada e a suite possui teste arquitetural atuando como barreira de engenharia contra o uso direto de metodos do Playwright (`.click()`, `.fill()`, `.goto()`, `.press()`, `.type()`, `.evaluate()`) fora dos arquivos permitidos.

## O que o agente pode fazer

1. Abrir sessao com login manual do usuario.
2. Ler processo aberto sob supervisao.
3. Confirmar numero do processo.
4. Ler arvore de documentos.
5. Ler conteudo visivel.
6. Resumir o processo.
7. Classificar o assunto.
8. Detectar prazos.
9. Sugerir providencia.
10. Gerar minuta fora do SEI.
11. Preparar pacote de revisao humana com Control Plane.
12. Propor evento de agenda ou alerta apenas como `ActionProposal`, com aprovacao humana quando houver efeito externo.

## O que o agente nunca deve fazer

1. Guardar senha.
2. Capturar cookie, token ou sessao.
3. Persistir perfil do navegador.
4. Assinar documento.
5. Tramitar processo.
6. Enviar processo.
7. Concluir processo.
8. Dar ciencia.
9. Cancelar documento.
10. Excluir documento.
11. Liberar acesso externo.
12. Enviar e-mail pelo SEI.
13. Criar tipo de documento no cadastro administrativo do SEI.
14. Criar, assinar ou enviar documento oficial sem acao humana.

Terminologia correta: quando a escrita real for homologada, o objetivo sera **criar uma minuta usando um tipo de documento ja existente no SEI**, nunca criar tipo de documento administrativo.

## Seguranca

Controles obrigatorios:

1. Allow-list/default-deny para qualquer acao.
2. Chokepoint para leitura do SEI.
3. `ReadOnlyPage` para separar leitura de escrita.
4. `MinutaWriter` como unico ponto de minuta controlada.
5. Token de confirmacao antes de minuta.
6. Verificacao do processo certo antes de qualquer escrita.
7. Hash de conteudo para amarrar aprovacao ao texto revisado.
8. Feature flags desligadas por padrao.
9. Auditoria sem texto integral.
10. Sessao efemera do navegador.
11. Bloqueio permanente de credenciais, cookies, sessoes e atos oficiais.
12. `ActionProposal` obrigatorio antes de qualquer acao externa.
13. `ApprovalRequest` obrigatorio para efeitos externos.
14. `DecisionRecord` obrigatorio para rastrear permitidos, bloqueios e revisoes.

## Variaveis de ambiente

Exemplo minimo recomendado para manter o modo seguro:

```env
APP_ENV=local
ENABLE_SEI_BROWSER_AUTOMATION=false
ENABLE_MINUTA_CREATION=false
MINUTA_TOKEN_SECRET=dev-insecure-trocar-em-producao
LOG_FULL_TEXT=false
ALLOW_OFFICIAL_SEI_ACTIONS=false
SEI_STORE_PASSWORDS=false
SEI_TEXT_RETENTION=ephemeral
```

Em producao/homologacao real, `MINUTA_TOKEN_SECRET` deve ser trocado por segredo local forte e nunca versionado.

## Roadmap

| Fase | Status | Descricao |
| --- | --- | --- |
| FASE 4 | Em desenvolvimento/supervisionada | Leitura e analise supervisionada do SEI com sessao manual do usuario. |
| FASE 5A | Implementada como simulacao segura | Minuta controlada simulada, sem escrita real no SEI. |
| FASE 5B | Futura | Escrita real de minuta, com seletores homologados, parando antes de qualquer ato oficial. |
| FASE 6 | Futura | Integracao com agenda e notificacoes dentro dos limites gratuitos/autorizados. |
| FASE 7 | Futura | Hardening, auditoria final, testes arquiteturais e revisao de seguranca. |
| FASE 58 | Planejada | Mission Queue persistente para missoes pendentes, em analise, prontas e bloqueadas. |
| FASE 59 | Implementada parcialmente | ActionProposal Engine e Tool Registry com guard central. |
| FASE 60 | Planejada | Approval Center para revisao humana antes de efeito externo. |
| FASE 61 | Planejada | Agent Memory sanitizada por missao, sem texto integral. |
| FASE 62 | Implementada parcialmente | Observability local e tracing operacional sanitizado. |
| FASE 63 | Planejada | Evaluation Harness com casos anonimizados. |
| FASE 64 | Em implementacao | Multi-task UX e painel de missoes supervisionadas. |

## UI do Agente 19

O formato aprovado para o Agente 19 na tela do SEI e um **chat lateral flutuante**, acionado por botao compacto dentro da pagina do SEI.

O chat permite perguntar sobre o processo aberto, capturar texto visivel ou selecionado, pedir resumo, prazos e providencia sugerida. Ele continua read-only: nao faz login, nao captura credenciais, nao clica no SEI e nao pratica ato oficial.

UI chat V2:

1. Mostra status fixo `Somente leitura`, `Backend local` e `Revisao humana`.
2. Permite acao rapida `Minuta` apenas como rascunho externo.
3. Informa que a insercao no SEI permanece manual.
4. Fecha pelo atalho `Esc`.
5. Continua sem clicar no SEI, sem preencher SEI e sem praticar ato oficial.

## FASE 5B-Homologacao

Status: preparada, sem escrita real.

1. Cadastro da minuta (`app/sei/minuta_cadastro.py`) exige `tipo_documento`, `nivel_acesso` e `text_hash`.
2. Acesso restrito/sigiloso exige `hipotese_legal`.
3. Campos `descricao`, `interessado` e `destinatario` podem ser exigidos por tipo documental.
4. Manifesto de seletores exige todos os seletores minimos homologados. Avaliador de prontidao em `app/sei/fase5b_homologacao.py` e modulo apenas de homologacao futura, nao de producao.
5. Seletores relacionados a assinar, tramitar, enviar, concluir, ciencia, cancelar, excluir ou liberar acesso externo sao bloqueados.
6. Mesmo quando tudo estiver pronto para homologacao, `real_write_allowed=false`.

## Como executar localmente

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe scripts\check_no_secrets.py .
.venv\Scripts\python.exe -m pytest
```

Painel local:

```bat
.venv\Scripts\python.exe -m app.dashboard
```

Agente 19 Desktop:

```bat
.venv\Scripts\python.exe -m app.desktop
```

## Documentacao

| Arquivo | Conteudo |
| --- | --- |
| [docs/00-visao-geral.md](docs/00-visao-geral.md) | Visao do produto, problema, usuarios e escopo |
| [docs/01-arquitetura.md](docs/01-arquitetura.md) | Modulos, fluxo tecnico, web app e agentes |
| [docs/02-regras-de-seguranca.md](docs/02-regras-de-seguranca.md) | Permissoes, acoes proibidas e guardas |
| [docs/03-manual-operacional.md](docs/03-manual-operacional.md) | Como operar o agente na rotina administrativa |
| [docs/04-google-agenda.md](docs/04-google-agenda.md) | Padrao de eventos, observacoes, convidados e duplicidade |
| [docs/05-alertas-celular.md](docs/05-alertas-celular.md) | Telegram, e-mail, WhatsApp futuro e modelo de alerta |
| [docs/06-integracao-sei.md](docs/06-integracao-sei.md) | Integracao assistida com SEI e limites de automacao |
| [docs/07-modelos-de-minutas.md](docs/07-modelos-de-minutas.md) | Modelos iniciais de minutas administrativas |
| [docs/08-roadmap.md](docs/08-roadmap.md) | Etapas de evolucao do projeto |
| [docs/57-orquestrador-missao-agente19.md](docs/57-orquestrador-missao-agente19.md) | Orquestrador de missao supervisionada do Agente 19 |
| [docs/58-mission-queue-control-plane.md](docs/58-mission-queue-control-plane.md) | Control Plane, Mission Queue, Approval Center e Evaluation Harness |
| [docs/61-nucleo-agente-ia-agente19.md](docs/61-nucleo-agente-ia-agente19.md) | Nucleo explicito de Agente de IA do Agente 19 |
| [docs/62-tracing-ferramentas-agente19.md](docs/62-tracing-ferramentas-agente19.md) | Tracing operacional e ferramentas seguras do Agente 19 |
| [docs/63-knowledge-base-inicial-19crpm.md](docs/63-knowledge-base-inicial-19crpm.md) | Knowledge base inicial e evidencias de regra do Agente 19 |

## Estrutura-alvo

```text
agente-sei-inteligente/
├── README.md
├── .env.example
├── docs/
├── app/
│   ├── agent/
│   ├── core/
│   ├── intake/
│   ├── intelligence/
│   ├── integrations/
│   ├── sei/
│   ├── storage/
│   ├── workers/
│   └── dashboard/
├── knowledge_base/
├── tests/
└── scripts/
```

## Stack recomendada

| Camada | Opcao inicial |
| --- | --- |
| Backend | Python com FastAPI |
| Interface web | Streamlit para MVP ou React/Next.js para produto final |
| Banco inicial | SQLite |
| Banco futuro | PostgreSQL |
| Fila simples | APScheduler ou RQ |
| PDF | PyMuPDF ou pdfplumber |
| E-mail | IMAP, Gmail API ou Microsoft Graph, conforme conta institucional |
| Agenda | Google Calendar API |
| Alertas | Telegram Bot API |
| Automacao web assistida | Playwright, sempre protegido por guarda de acoes |
| IA | Provedor configuravel, com opcao local ou API externa |

## Regra de ouro

O usuario humano continua no controle. O agente pode ler, resumir, classificar, sugerir providencia, gerar minuta e preparar missoes supervisionadas. Atos oficiais no SEI permanecem manuais: assinatura, envio, tramitacao, conclusao, ciencia, cancelamento, exclusao e liberacao de acesso externo ficam fora do agente.
