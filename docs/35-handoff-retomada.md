# Handoff e retomada do desenvolvimento

Documento de continuidade: onde o desenvolvimento parou e como retomar em outra
estacao de trabalho.

Ultima atualizacao: 2026-06-23
Branch de trabalho: `feat/fundacao-agenda-ics`
Repositorio: https://github.com/welitonsp/agente-sei-inteligente

## Retomada rapida — sessao 2026-07-08 (LEIA PRIMEIRO)

Tudo abaixo JA ESTA NO `main` (fila de PRs zerada). Suite verde. Ao rodar testes,
valide em modo "CI-safe": `DATABASE_URL` apontando para um diretorio inexistente
(o CI nao tem a pasta `data/`), para pegar testes que precisam de banco.

Entregue nesta sessao (na ordem, tudo mergeado):

1. **Auditoria do nucleo de IA** — grafo roteado por `app/intelligence/ai_reasoning.py`
   (Claude via `ai_provider`), critico FAIL-CLOSED, `audit_node` persiste auditoria
   real, confianca do Shadow Mode normalizada 0..1. `llm_gemini.py` removido.
2. **Alertas Telegram (dry-run)** — `app/integrations/telegram_service.py` (inerte
   sem token/chat) + `docs/64-plano-de-sucesso.md` + esqueleto da KB do 19 CRPM
   (`knowledge_base/fluxos_19crpm/COMO_PREENCHER.md`).
3. **Inteligencia dos manuais** — `app/intelligence/manual_retriever.py` (RAG local)
   sobre `knowledge_base/manual_sei/` e `knowledge_base/redacao_goias/`, ligado ao
   `rag_node`; `app/intelligence/redacao_goias_policy.py` (guardrail de redacao).
4. **Runtime de ferramentas guardado** — `app/agent/tool_runtime.py` (catalogo tipo
   n8n com allow-list + guard + auditoria por chamada).
5. **Loop de tool-calling com Claude** — `app/agent/tool_calling_agent.py` (o modelo
   escolhe/invoca ferramentas; cada chamada passa pelo runtime/guard).

**Proximo passo (escolher):**
- (A) **Cockpit da FASE 65** (`docs/65`, PR 1): UI da missao (timeline + evidencias +
  editor de minuta), Modo 1 Manual seguro, sem automacao no SEI. Maior impacto visivel.
- (B) Ampliar o `tool_runtime` com `alertar_prazo` (Telegram ja no main) e fiar o
  agente/policy ao grafo/cockpit.

**Gargalo que depende do usuario (nao e codigo):** preencher a KB real do 19 CRPM
(unidades, regras, palavras-chave) + 5 casos anonimizados. Sem isso a triagem fica
limitada.

---

> Observacao de processo: o padrao de branch definido em `docs/28` e
> `codex/<tipo>-<descricao>`. A branch atual usa o prefixo `feat/`; manter assim
> ate o merge para nao quebrar referencias ja publicadas. Proximas branches
> devem seguir o padrao `codex/`.

## O que ja esta pronto (commitado e no GitHub)

| Area | Estado | Arquivos principais |
| --- | --- | --- |
| Fundacao tecnica (seguranca) | CONCLUIDO | `app/core/permissions.py`, `app/sei/sei_action_guard.py`, `app/core/security_filter.py`, `app/core/audit.py`, `app/core/config.py`, `app/core/logging.py` |
| Banco de dados (8 entidades) | CONCLUIDO | `app/storage/db.py`, `app/storage/models.py` |
| Agenda Oficiais | CONCLUIDO (dry-run) | `app/integrations/agenda_service.py`, `app/integrations/calendar_backend.py` |
| Convidados via marcador OFICIAIS | CONCLUIDO | `app/integrations/contacts_resolver.py` |
| Dedup contra calendario real (ICS) | CONCLUIDO | `app/integrations/ics_reader.py` |
| Cliente OAuth real (Calendar+People) | Codigo pronto | `app/integrations/google_auth.py`, `app/integrations/runtime.py` |
| Intake texto manual | CONCLUIDO no backend | `app/intake/manual_text.py`, `tests/test_manual_text_intake.py` |
| Intake PDF local | CONCLUIDO para PDF pesquisavel | `app/intake/pdf_upload.py`, `tests/test_pdf_upload_intake.py` |
| Painel local texto/PDF | CONCLUIDO para MVP texto/PDF | `app/dashboard/local_app.py`, `tests/test_dashboard_local_app.py` |
| Extensao SEI read-only | PROTOTIPO chat lateral V2 | `browser_extension/`, `tests/test_browser_extension_contract.py`, `docs/43-ui-chat-agente19-sei.md`, `docs/44-preview-local-ui-chat-agente19.md`, `docs/45-ux-chat-v2-minuta-externa.md` |
| Agente 19 Desktop seguro | PROTOTIPO | `app/desktop/`, `tests/test_desktop_secure_browser.py` |
| Minutador local zero custo | PROTOTIPO | `app/intelligence/local_minutador.py`, `knowledge_base/templates_minutas/`, `tests/test_local_minutador.py` |
| Knowledge base local 19 CRPM | PROTOTIPO sem dados reais | `knowledge_base/fluxos_19crpm/`, `app/intelligence/knowledge_base.py`, `app/intelligence/local_triage.py` |
| Enquadramento SEI particular/local | DOCUMENTADO | `README.md`, `docs/fase-5-minuta-controlada.md`, `docs/06-integracao-sei.md` |
| PATCH 4 hardening FASE 5A | CONCLUIDO | `app/core/safety.py`, `app/sei/minuta_writer.py`, `tests/test_phase5a_minuta_controlada.py` |
| FASE 5B-homologacao | CONCLUIDO sem escrita real | `app/sei/minuta_cadastro.py`, `app/sei/selector_manifest.py`, `app/sei/fase5b_homologacao.py` |
| Diagnostico API SEI/WSSEI | CONCLUIDO; sem API publica utilizavel | `app/sei/api_discovery.py`, `scripts/sei_api_discovery.py`, `docs/42-resultado-diagnostico-real-api-sei.md` |
| Scripts | CONCLUIDO | `scripts/init_db.py`, `scripts/google_oauth_setup.py`, `scripts/google_validate.py` |
| PR e CI | PR #1 draft aberto; CI aprovado | https://github.com/welitonsp/agente-sei-inteligente/pull/1 |
| Gate de segredos | CONCLUIDO | `.github/workflows/ci.yml`, `scripts/check_no_secrets.py` |
| Testes | 150 passando | `tests/` |

Modo atual: **dry-run** (simulacao). Nenhum evento real e criado ate o OAuth
estar completo no `.env`.

## Onde paramos exatamente: configuracao OAuth do Google

1. [x] Projeto criado no Google Cloud Console.
2. [x] APIs ativadas: Google Calendar API e People API.
3. [x] Tela de consentimento OAuth criada (tipo Externo).
4. [x] Credencial OAuth "Desktop app" criada.
5. [x] `GOOGLE_CLIENT_ID` colocado no `.env` local.
6. [ ] **PENDENTE:** publicar o app (recomendado) OU adicionar test user
       `19crpm.pm@gmail.com` (sem publicar, o refresh token expira em 7 dias).
7. [ ] **PENDENTE:** colar `GOOGLE_CLIENT_SECRET` no `.env`.
8. [ ] **PENDENTE:** rodar `scripts/google_oauth_setup.py`, autorizar com
       `19crpm.pm@gmail.com` e colar o `GOOGLE_REFRESH_TOKEN` no `.env`.
9. [ ] **PENDENTE:** rodar `scripts/google_validate.py` (validacao read-only).

Client ID (nao e segredo):
`684199514457-77evd2bapi8vk6c61v0ntdt3541nrpop.apps.googleusercontent.com`

## Como retomar em outra estacao de trabalho

### 1. Clonar e entrar na branch

```bat
git clone https://github.com/welitonsp/agente-sei-inteligente.git
cd agente-sei-inteligente
git checkout feat/fundacao-agenda-ics
```

### 2. Criar ambiente e instalar dependencias

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Recriar o `.env` (NAO vai para o Git; contem segredos)

```bat
copy .env.example .env
```

Depois edite o `.env` e preencha. Os SEGREDOS nao estao no repositorio; traga-os
da estacao anterior por canal seguro OU obtenha novamente:

| Variavel | Onde obter |
| --- | --- |
| `GOOGLE_CALENDAR_ID` | `19crpm.pm@gmail.com` |
| `GOOGLE_CALENDAR_ICS_URL` | Google Agenda -> Config. da agenda -> Endereco secreto iCal |
| `GOOGLE_CLIENT_ID` | Ver acima (nao e segredo) |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console -> Credenciais -> cliente Desktop |
| `GOOGLE_REFRESH_TOKEN` | Gerar com `scripts/google_oauth_setup.py` |
| `CALENDAR_BACKEND` | `google` (real) ou `dry_run` (simulacao) |
| `OFFICERS_SOURCE` | `google_contacts` |
| `OFFICERS_CONTACT_LABEL` | `OFICIAIS` |
| `ENABLE_SEI_BROWSER_AUTOMATION` | `false` por padrao |
| `ENABLE_MINUTA_CREATION` | `false` por padrao |
| `MINUTA_TOKEN_SECRET` | trocar em ambiente real; nunca versionar segredo forte |
| `LOG_FULL_TEXT` | `false` por padrao |

### 4. Inicializar o banco e rodar os testes

```bat
set PYTHONPATH=.
.venv\Scripts\python.exe scripts\init_db.py
.venv\Scripts\python.exe scripts\check_no_secrets.py .
.venv\Scripts\python.exe -m pytest
```

Esperado: scanner sem segredos concretos e 150 testes passando.

### 4.1. Rodar o painel MVP local

```bat
.venv\Scripts\python.exe -m app.dashboard
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

### 4.2. Rodar o Agente 19 Desktop

```bat
.venv\Scripts\python.exe -m app.desktop
```

O desktop abre uma janela local do Agente 19, sobe o backend local se necessario
e oferece botao para abrir o SEI na URL oficial `https://sei.go.gov.br/sei/`.
O login acontece somente na pagina oficial do SEI. O Agente 19 nao captura
senha, cookie, sessao ou credenciais, nao clica no SEI e nao pratica atos
oficiais.

### 4.3. Testar extensao no navegador

1. Rode o backend local:

```bat
.venv\Scripts\python.exe -m app.dashboard
```

2. No Chrome/Edge, abra `chrome://extensions` ou `edge://extensions`.
3. Ative "Modo do desenvolvedor".
4. Carregue sem compactacao a pasta `browser_extension/`.
5. Abra uma pagina do SEI ja autenticada manualmente e clique em `Agente 19`.

Regras: a extensao e read-only, nao faz login, nao guarda senha/cookie, nao
clica no SEI e envia somente texto visivel/selecionado ao backend local.

Formato atual: chat lateral profissional com botao flutuante `19`, historico de
mensagens, pergunta livre, captura de tela e acoes rapidas de resumo, prazos e
providencia.

Preview local:

```text
C:\ADM PMGO\browser_extension\preview_chat.html
```

### 5. Concluir o OAuth (itens pendentes acima)

```bat
.venv\Scripts\python.exe scripts\google_oauth_setup.py
.venv\Scripts\python.exe scripts\google_validate.py
```

Autorize com `19crpm.pm@gmail.com` (a conta com o marcador OFICIAIS e acesso de
escrita a agenda). Cole o refresh token impresso no `.env`.

## Regras de seguranca que continuam valendo

1. `.env`, segredos e tokens NUNCA vao para o Git (cobertos pelo `.gitignore`).
2. URL do ICS, client secret e refresh token sao segredos: somente no `.env`.
3. O agente permanece em dry-run ate o OAuth completo; criar evento exige
   aprovacao humana (guard) e o ICS so faz leitura.
4. Se algum segredo vazar, revogar em https://myaccount.google.com/permissions.
5. O login no SEI e manual; o agente nao guarda senha, cookie, token ou sessao.
6. Sessao Playwright deve ser efemera e sem perfil persistido.
7. LLM nao controla navegador; interacao com SEI deve ser codigo deterministico e auditado.

## PATCH 4 aplicado

1. `MINUTA_TOKEN_SECRET` padrao bloqueado em `APP_ENV=prod`.
2. `ENABLE_MINUTA_CREATION=true` bloqueado em producao enquanto FASE 5B nao estiver homologada.
3. Auditoria registra `text_hash`, nunca texto integral.
4. Teste arquitetural contra uso direto de Playwright fora dos arquivos permitidos criado.
5. Escrita real mantida como `NotImplementedError`.

## Proximo passo imediato - FASE 5B em homologacao

1. Preencher `knowledge_base/sei_homologacao/minuta_selectors.template.json` somente em homologacao controlada.
2. Registrar evidencia de cada seletor.
3. Validar tipo de documento ja existente.
4. Validar nivel de acesso, descricao, interessado e destinatario quando aplicavel.
5. Manter `real_write_allowed=false` ate aceite formal.
6. Nunca assinar, tramitar, enviar, concluir, dar ciencia, cancelar, excluir ou liberar acesso externo.

## Diagnostico seguro de API SEI/WSSEI

```bat
.venv\Scripts\python.exe scripts\sei_api_discovery.py
```

Regras: nao envia credenciais, nao usa sessao do navegador, nao executa operacao
de negocio e resultado positivo nao autoriza uso real.

Resultado em 2026-06-23: `mod-wssei-v2` e `mod-wssei-v1` retornaram 404; WSDL
nativo ficou indisponivel com conexao encerrada pelo host remoto.

## Proximo passo apos validar o OAuth

1. `google_validate.py` confirmando os contatos do marcador OFICIAIS.
2. Primeiro evento real de teste com aprovacao humana e convite aos OFICIAIS.
3. Registrar a homologacao em `docs/32-registro-testes-homologacao.md`.
4. Depois: Etapa C (Telegram) e/ou painel web acionando
   `manual_text.analyze_text` e `runtime.schedule_official_event`.
