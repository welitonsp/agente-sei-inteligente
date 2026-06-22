# Changelog

Todas as entregas relevantes do projeto devem ser registradas aqui.

## [0.3.7-knowledge-base-local-19crpm] - 2026-06-22

### Adicionado

1. Estrutura `knowledge_base/fluxos_19crpm/` com CSVs locais.
2. Carregador em `app/intelligence/knowledge_base.py`.
3. Triagem e roteamento por regras em `app/intelligence/local_triage.py`.
4. Endpoint local `POST /api/triage-local`.
5. Botao `Triagem local` no painel e no desktop.
6. Documento da Fase 40 em `docs/40-fase-knowledge-base-local-19crpm.md`.
7. Testes automatizados em `tests/test_local_knowledge_base.py`.

### Seguranca

1. Sem regras reais, o sistema retorna `indefinido`.
2. Unidade responsavel nao e inventada.
3. Sugestao exige revisao humana obrigatoria.
4. A triagem nao executa ato oficial no SEI.

## [0.3.6-minutador-local-zero-custo] - 2026-06-22

### Adicionado

1. Minutador local em `app/intelligence/local_minutador.py`.
2. Templates locais em `knowledge_base/templates_minutas/`.
3. Endpoint local `POST /api/generate-draft`.
4. Botao `Gerar minuta local` no painel MVP.
5. Botao `Gerar minuta` no Agente 19 Desktop.
6. Documento da Fase 39 em `docs/39-fase-minutador-local-zero-custo.md`.
7. Testes automatizados em `tests/test_local_minutador.py`.

### Seguranca

1. Minutas sao rascunhos locais e exigem revisao humana.
2. O sistema nao escreve no SEI, nao cria documento oficial e nao assina.
3. Auditoria registra metadados, tipo e confianca, sem persistir texto integral.
4. Acoes oficiais permanecem bloqueadas no contrato.

## [0.3.5-estrategia-zero-custo] - 2026-06-22

### Adicionado

1. Estrategia zero custo em `docs/38-estrategia-zero-custo-sei.md`.
2. Decisao DEC-0012 registrando que o projeto nao deve depender de servico
   pago, API paga, assinatura, RPA pago ou hospedagem paga.

### Alterado

1. Caminho de IA passa a priorizar regras locais, templates, OCR gratuito e
   modelo local opcional, conforme hardware e autorizacao.
2. Minutador por templates locais passa a ser a proxima entrega recomendada
   antes de qualquer IA paga.

### Seguranca

1. Conteudo real do SEI continua proibido em IA externa sem autorizacao formal.
2. Escrita no SEI continua proibida sem homologacao; quando liberada, no maximo
   minuta/rascunho sem assinatura.

## [0.3.4-desktop-navegador-seguro] - 2026-06-22

### Adicionado

1. Aplicacao desktop local em `app/desktop/`, executavel com
   `.venv\Scripts\python.exe -m app.desktop`.
2. Botao para abrir a URL oficial `https://sei.go.gov.br/sei/` em
   navegador/janela separada, sem capturar login ou senha.
3. Painel desktop do Agente 19 para texto colado, PDF manual, resumo, tipo
   provavel, evento/prazo, providencia sugerida e copia do resultado.
4. Comunicacao do desktop restrita ao backend local `http://127.0.0.1:8000`.
5. Documento da Fase 37.2 em `docs/37-fase-desktop-navegador-seguro.md`.
6. Testes de contrato de seguranca do desktop em
   `tests/test_desktop_secure_browser.py`.

### Seguranca

1. O Agente 19 Desktop nao possui campo de senha ou login SEI.
2. Payloads com campos/indicios de credencial sao bloqueados.
3. O desktop nao le cookies, sessao, localStorage/sessionStorage ou headers de
   autenticacao.
4. O desktop nao executa cliques nem atos oficiais no SEI.
5. A extensao Chrome/Edge fica como recurso futuro opcional, dependente de
   autorizacao institucional.

### Riscos conhecidos

1. Uso real com navegador interno ou janela separada depende de homologacao e
   autorizacao institucional.
2. O usuario ainda precisa copiar texto/exportar PDF manualmente do SEI.

## [0.3.3-extensao-sei-readonly] - 2026-06-22

### Adicionado

1. Protótipo de extensão Chrome/Edge em `browser_extension/`, com botão
   flutuante dentro das páginas `https://sei.go.gov.br/sei/*`.
2. Painel lateral in-page para capturar texto visível/selecionado da tela do
   SEI e enviar ao backend local `POST /api/import-text`.
3. Service worker `background.js` chamando apenas `http://127.0.0.1:8000`.
4. Testes de contrato de segurança da extensão
   (`tests/test_browser_extension_contract.py`).
5. Relatorio consolidado de status do projeto em
   `docs/36-relatorio-status-projeto.md`.

### Segurança

1. Extensão não solicita permissão de cookies nem webRequest.
2. Extensão não guarda senha, cookie ou sessão.
3. Extensão não executa clique automático no SEI.
4. Termos de atos oficiais são bloqueados no conteúdo enviado para análise.
5. Modo continua read-only e exige revisão humana.

### Riscos conhecidos

1. Requer instalação manual como extensão sem publicação na loja.
2. Leitura direta da tela do SEI deve ser validada em homologação institucional.
3. Busca/navegação por número de processo e qualquer ato oficial seguem proibidos.

## [0.3.2-pdf-local] - 2026-06-22

### Adicionado

1. Upload/análise local de PDF em `app/intake/pdf_upload.py`, usando `pypdf`
   para extrair texto de PDFs pesquisáveis.
2. Detecção de PDF sem texto extraível, com `status_leitura=ocr_necessario`.
3. Endpoint local `POST /api/import-pdf` e campo de upload no painel MVP.
4. Persistência segura de hash/metadados/resumo estrutural de PDF, sem salvar
   texto integral.
5. Testes automatizados do fluxo PDF (`tests/test_pdf_upload_intake.py`).

### Alterado

1. `requirements.txt`: adiciona `pypdf`.
2. Painel local passa a aceitar texto colado ou PDF.

### Segurança

1. Upload PDF passa pelo guardião antes de leitura/resumo.
2. Auditoria registra hash, quantidade de páginas e contagem de caracteres, sem
   registrar texto integral.
3. Suite local ampliada para 97 testes passando.

### Riscos conhecidos

1. OCR ainda não executa reconhecimento; apenas marca `ocr_necessario`.
2. Autenticação do painel local continua pendente.
3. Triagem real do 19 CRPM segue bloqueada até preencher a knowledge base.

## [0.3.1-painel-local-texto] - 2026-06-22

### Adicionado

1. Painel MVP local em `app/dashboard/local_app.py`, sem dependencias externas,
   executavel com `python -m app.dashboard`.
2. Tela operacional para numero do processo SEI, usuario local, titulo, texto
   copiado, botao de analise e exibicao do resultado estruturado.
3. Endpoint local `POST /api/import-text`, conectado ao backend
   `manual_text.analyze_text`.
4. Testes automatizados do painel local (`tests/test_dashboard_local_app.py`).

### Seguranca

1. Painel nao acessa SEI real, nao pesquisa processo por numero e nao oferece
   botoes de ato oficial.
2. Resultado exibe revisao humana obrigatoria e campos pendentes.
3. Suite local ampliada para 92 testes passando.

### Riscos conhecidos

1. Painel ainda nao tem autenticacao; permitido apenas para MVP local.
2. Upload de PDF/OCR ainda nao implementado.
3. Triagem real do 19 CRPM segue bloqueada ate preencher a knowledge base.

## [0.3-intake-texto-local] - 2026-06-22

### Adicionado

1. Fluxo backend `IMPORT_TEXT` em `app/intake/manual_text.py` para receber texto
   colado no MVP externo/local, sem acessar o SEI real.
2. Persistencia segura de metadados em `Process` e `Document`: hash do texto,
   titulo, origem, classificacao e resumo estrutural; texto integral nao e
   persistido por padrao.
3. Extracao local simples de evento, prazo, data, horario e local para apoiar a
   futura tela de revisao administrativa.
4. Testes automatizados do intake manual (`tests/test_manual_text_intake.py`).

### Seguranca

1. Fluxo passa pelo guardiao (`LER_DOCUMENTO` e `RESUMIR`) antes de registrar a
   analise.
2. Auditoria registra metadados, hash e contagens, sem gravar o texto colado.
3. Toda analise local retorna `revisao_humana_obrigatoria=true`.
4. Suite local ampliada para 89 testes passando.

### Riscos conhecidos

1. Ainda nao ha tela web consumindo o backend de texto colado.
2. Extracao e heuristica; baixa confianca permanece em revisao humana.
3. PDF, OCR, IA/RAG e triagem 19 CRPM real continuam pendentes.

## [0.2.1-ci-gate] - 2026-06-22

### Adicionado

1. Workflow GitHub Actions em `.github/workflows/ci.yml` para rodar testes em
   Python 3.11 e 3.13.
2. Gate simples de segredos em `scripts/check_no_secrets.py`, varrendo arquivos
   conhecidos pelo Git e novos nao ignorados, bloqueando `.env`, refresh token,
   client secret, URL ICS, chaves de API e private keys concretas.
3. Testes automatizados do scanner de segredos (`tests/test_secret_scanner.py`).

### Seguranca

1. CI passa a executar `scripts/check_no_secrets.py` antes do `pytest`.
2. Varredura local confirmou ausencia de segredos concretos nos arquivos
   conhecidos pelo Git e novos nao ignorados.
3. Suite local ampliada para 84 testes passando.

### Riscos conhecidos

1. PR #1 aberto em modo draft e GitHub Actions aprovado em Python 3.11/3.13.
2. Protecao de branch ainda precisa ser configurada no GitHub.
3. OAuth do Google continua pendente de conclusao (client secret + refresh token).

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

1. CI no GitHub Actions configurado em 2026-06-22 e aprovado no PR #1.
2. Knowledge base do 19 CRPM ainda usa templates.
3. OAuth do Google pendente de conclusao (client secret + refresh token).
4. PR #1 aberto em modo draft; merge para `main` pendente de revisao humana.

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
