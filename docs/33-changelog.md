# Changelog

Todas as entregas relevantes do projeto devem ser registradas aqui.

## [0.2-fundacao-tecnica] - 2026-06-21

### Adicionado

1. Estrutura `app/` e fundacao tecnica de seguranca:
   `permissions.py` (lista positiva/proibida/sensivel), `sei_action_guard.py`
   (guardiao com negacao por padrao), `security_filter.py` (sanitiza segredos),
   `config.py`, `logging.py` e `audit.py`.
2. Banco SQLite com as 8 entidades de `docs/11` (`storage/db.py`, `models.py`).
3. Skill `agenda-oficiais` (`integrations/agenda_service.py`): titulo padrao,
   observacao, lembretes por tipo, dedup local e guard com aprovacao humana.
4. Backends de calendario: `InMemory` (dry-run) e `Google` (OAuth, import tardio).
5. Resolucao de convidados pelo marcador "OFICIAIS" via People API
   (`integrations/contacts_resolver.py`).
6. Leitor iCal read-only e dedup contra o calendario real
   (`integrations/ics_reader.py`, `find_equivalent`).
7. Cliente OAuth real Calendar+People (`integrations/google_auth.py`,
   `integrations/runtime.py`) e scripts `google_oauth_setup.py`,
   `google_validate.py`, `init_db.py`.
8. Suite de testes (81 casos) e documento de handoff `docs/35`.

### Alterado

1. `.env.example`: variaveis de OAuth, `CALENDAR_BACKEND`, `OFFICERS_SOURCE`,
   `OFFICERS_CONTACT_LABEL`, `GOOGLE_CALENDAR_ICS_URL`.
2. `.gitignore`: ignora arquivos de credencial/token Google.

### Segurança

1. Atos oficiais do SEI bloqueados no `sei_action_guard.py` (gate testado).
2. Senha/cookie/token/URL ICS sanitizados antes de log e auditoria.
3. Refresh token e client secret tratados como segredos (somente `.env`).
4. Convites e e-mails dos Oficiais: auditoria registra so a contagem.
5. Modo dry-run permanece como padrao ate o OAuth completo.

### Riscos conhecidos

1. CI no GitHub Actions ainda nao configurado (gate roda apenas local).
2. Knowledge base do 19 CRPM ainda usa templates.
3. OAuth do Google pendente de conclusao (client secret + refresh token).
4. Sem PR aberto ainda; merge para `main` pendente de revisao humana.

## [0.1-docs] - 2026-06-21

### Adicionado

1. Documentacao base do Agente SEI Inteligente.
2. Politicas de seguranca, identidade, dados e SEI.
3. Estrategia sem modulo oficial SEI IA.
4. Requisito do robozinho SEI.
5. Skills especialistas e contratos.
6. Matriz de conformidade.
7. Checklist de processos de desenvolvimento.
8. Regras de Git, IA, Commit, Push, PR e Merge.
9. Regra de documentacao continua.
10. Prompt mestre para Claude Code.

### Alterado

1. README atualizado com indice documental.

### Segurança

1. Atos oficiais no SEI bloqueados por politica.
2. Conteudo real do SEI proibido em IA externa sem autorizacao formal.
3. Usuario/senha individuais preservados.

### Riscos conhecidos

1. Nao ha codigo de aplicacao.
2. Knowledge base do 19 CRPM ainda usa templates.
3. Robozinho real/extensao esta fora do MVP.
