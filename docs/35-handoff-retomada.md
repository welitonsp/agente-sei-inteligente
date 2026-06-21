# Handoff e retomada do desenvolvimento

Documento de continuidade: onde o desenvolvimento parou e como retomar em outra
estacao de trabalho.

Ultima atualizacao: 2026-06-21
Branch de trabalho: `feat/fundacao-agenda-ics`
Repositorio: https://github.com/welitonsp/agente-sei-inteligente

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
| Scripts | CONCLUIDO | `scripts/init_db.py`, `scripts/google_oauth_setup.py`, `scripts/google_validate.py` |
| Testes | 81 passando | `tests/` |

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

### 4. Inicializar o banco e rodar os testes

```bat
set PYTHONPATH=.
.venv\Scripts\python.exe scripts\init_db.py
.venv\Scripts\python.exe -m pytest
```

Esperado: 81 testes passando.

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

## Proximo passo apos validar o OAuth

1. `google_validate.py` confirmando os contatos do marcador OFICIAIS.
2. Primeiro evento real de teste com aprovacao humana e convite aos OFICIAIS.
3. Registrar a homologacao em `docs/32-registro-testes-homologacao.md`.
4. Depois: Etapa C (Telegram) e/ou painel web acionando
   `runtime.schedule_official_event`.
