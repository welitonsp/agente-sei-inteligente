# Agente SEI Inteligente Particular (Agente 19) — Funcionário Digital de IA do 19º CRPM

Documentacao-base do projeto do Agente 19, o Funcionário Digital de IA criado para apoiar a rotina do 19º CRPM com e-mail institucional, PDF, Google Agenda, alertas em celular, minutas administrativas e uso assistido do SEI.

Versao documental: 0.4.7
Data: 2026-06-23
Status: arquitetura particular/local supervisionada, UI chat V2 do Agente 19 definida com preview local e minuta externa supervisionada, PATCH 4 aplicado, FASE 5B-homologacao preparada, diagnostico real de API SEI/WSSEI executado e escrita real no SEI ainda nao habilitada.

## Enquadramento

O Agente SEI Inteligente Particular, tambem chamado Agente 19, e uma solucao local/particular para apoiar o usuario enquanto ele trabalha no SEI Goias com sua propria conta.

Nao ha autorizacao de API oficial, WSSEI, modulo oficial SEI IA ou acesso de TI. Por isso, o projeto nao deve se apresentar como integracao institucional oficial. O usuario faz login manualmente no SEI, diretamente na pagina oficial, e o agente apenas apoia leitura, classificacao, resumo, providencias e minutas sob supervisao humana.

O agente prepara, organiza e sugere. Ele nao substitui o usuario logado, nao pratica ato oficial e nao assume responsabilidade administrativa.

**Regra-mãe**: O Agente 19 prepara, sugere, organiza, cria minuta e aprende. O humano revisa, assina e pratica o ato oficial.

O sistema não substitui a autoridade humana.

**Limites obrigatórios**: O Agente 19 NÃO pode:
- pedir senha do SEI;
- armazenar senha;
- armazenar cookie;
- armazenar sessão;
- capturar token;
- assinar documento;
- tramitar processo;
- concluir processo;
- excluir documento;
- cancelar documento;
- dar ciência automática;
- enviar processo automaticamente;
- praticar ato oficial final.

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

PATCH 4 aplicado: o startup valida ambiente seguro, a escrita real permanece bloqueada e a suite possui teste arquitetural atuando como barreira de engenharia contra o uso direto de metodos do Playwright (`.click()`, `.fill()`, `.goto()`, `.press()`, `.type()`, `.evaluate()`) fora dos arquivos permitidos.

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
11. Preparar criacao controlada de minuta no SEI, ainda simulada na FASE 5A.

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

## FASE 5 - Minuta controlada

### FASE 5A - arquitetura segura simulada

Objetivo: provar a arquitetura de escrita controlada sem escrever de fato no SEI.

Status aprovado:

1. `MinutaWriter` criado para centralizar qualquer tentativa de minuta.
2. Token de confirmacao amarrado a processo + tipo de documento + hash do texto.
3. Verificacao de processo correto antes de qualquer escrita.
4. Allow-list separada para escrita controlada.
5. Stubs com `NotImplementedError` para a UI real.
6. Nenhuma escrita real no SEI.
7. `ENABLE_MINUTA_CREATION=false` por padrao.

A FASE 5A serve para testar seguranca, rastreabilidade e bloqueios. Ela nao libera uso operacional de escrita no SEI.

### FASE 5B - futura

Somente depois de homologacao com seletores reais e autorizacao expressa, a FASE 5B podera criar uma minuta no SEI. O fluxo permitido sera:

1. Criar minuta real no SEI.
2. Selecionar tipo de documento ja existente.
3. Preencher cadastro.
4. Inserir texto no editor.
5. Salvar minuta.
6. Parar.

Mesmo na FASE 5B, continua proibido:

1. Assinar.
2. Tramitar.
3. Enviar.
4. Concluir.
5. Dar ciencia.
6. Cancelar.
7. Excluir.
8. Liberar acesso externo.

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

## PATCH 4 - hardening final

Status: executado.

1. `MINUTA_TOKEN_SECRET` padrao bloqueado em `APP_ENV=prod`.
2. `ENABLE_MINUTA_CREATION=true` bloqueado em producao enquanto FASE 5B nao estiver homologada.
3. Auditoria da FASE 5A registra `text_hash`, nunca texto integral.
4. Teste arquitetural criado contra uso direto de Playwright fora dos arquivos permitidos. Essa e uma barreira de engenharia rigida para garantir que nenhum desenvolvedor insira `.click()`, `.fill()`, `.type()`, `.press()` ou `.evaluate()` acidentalmente no fluxo de leitura e analise, garantindo a natureza read-only e o agente sempre supervisionado.
5. Escrita real mantida como `NotImplementedError`.

## Proximo passo imediato

Como o diagnostico real nao encontrou `mod-wssei` publico nos caminhos padrao, manter o desenvolvimento no caminho local supervisionado: leitura assistida, minuta local/controlada e homologacao da FASE 5B sem escrita real.

## UI do Agente 19

O formato aprovado para o Agente 19 na tela do SEI e um **chat lateral
flutuante**, acionado por botao compacto dentro da pagina do SEI.

O chat permite perguntar sobre o processo aberto, capturar texto visivel ou
selecionado, pedir resumo, prazos e providencia sugerida. Ele continua read-only:
nao faz login, nao captura credenciais, nao clica no SEI e nao pratica ato
oficial.

Previa local da interface:

```text
C:\ADM PMGO\browser_extension\preview_chat.html
```

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
4. Manifesto de seletores exige todos os seletores minimos homologados. Avaliador de prontidao em `app/sei/fase5b_homologacao.py` (modulo apenas de homologacao futura, nao de producao).
5. Seletores relacionados a assinar, tramitar, enviar, concluir, ciencia, cancelar, excluir ou liberar acesso externo sao bloqueados. Ferramentas de apoio como `app/sei/api_discovery.py` sao restritas a diagnostico local/nao-destrutivo.
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
| [docs/27-checklist-processos-desenvolvimento.md](docs/27-checklist-processos-desenvolvimento.md) | Checklist de processos para desenvolvimento |
| [docs/28-regras-git-ia.md](docs/28-regras-git-ia.md) | Regras de commit, push, PR e merge com uso de IA |
| [docs/29-regra-documentacao-continua.md](docs/29-regra-documentacao-continua.md) | Regra para documentar processos, decisoes e mudancas continuamente |
| [docs/30-registro-decisoes.md](docs/30-registro-decisoes.md) | Registro historico de decisoes arquiteturais e operacionais |
| [docs/31-registro-processos.md](docs/31-registro-processos.md) | Registro de mapeamentos de processos da unidade |
| [docs/32-registro-testes-homologacao.md](docs/32-registro-testes-homologacao.md) | Logs e resultados das sessoes de homologacao do Agente 19 |
| [docs/33-changelog.md](docs/33-changelog.md) | Changelog das entregas |
| [docs/34-prompt-claude-code.md](docs/34-prompt-claude-code.md) | Prompt mestre para executar o projeto |
| [docs/36-relatorio-status-projeto.md](docs/36-relatorio-status-projeto.md) | Relatorio consolidado do que foi feito e do que falta |
| [docs/fase-5-minuta-controlada.md](docs/fase-5-minuta-controlada.md) | FASE 5A/5B de minuta controlada |
| [docs/37-fase-desktop-navegador-seguro.md](docs/37-fase-desktop-navegador-seguro.md) | Agente 19 Desktop com navegador seguro |
| [docs/38-estrategia-zero-custo-sei.md](docs/38-estrategia-zero-custo-sei.md) | Estrategia zero custo |
| [docs/39-fase-minutador-local-zero-custo.md](docs/39-fase-minutador-local-zero-custo.md) | Minutador local zero custo |
| [docs/40-fase-knowledge-base-local-19crpm.md](docs/40-fase-knowledge-base-local-19crpm.md) | Knowledge base local do 19 CRPM |
| [docs/41-diagnostico-api-sei-wssei.md](docs/41-diagnostico-api-sei-wssei.md) | Diagnostico seguro de API SEI/WSSEI |
| [docs/42-resultado-diagnostico-real-api-sei.md](docs/42-resultado-diagnostico-real-api-sei.md) | Resultado real do diagnostico API SEI/WSSEI |
| [docs/43-ui-chat-agente19-sei.md](docs/43-ui-chat-agente19-sei.md) | UI chat do Agente 19 na tela do SEI |
| [docs/44-preview-local-ui-chat-agente19.md](docs/44-preview-local-ui-chat-agente19.md) | Preview local da UI chat |
| [docs/45-ux-chat-v2-minuta-externa.md](docs/45-ux-chat-v2-minuta-externa.md) | UX Chat V2 e minuta externa supervisionada |
| [docs/46-fase5b-homologacao-seletores.md](docs/46-fase5b-homologacao-seletores.md) | FASE 5B-H: Homologação de Seletores |
| [docs/47-seletores-descobertos-referencia.md](docs/47-seletores-descobertos-referencia.md) | Mapeamento Padrão Descoberto de Seletores |
| [docs/48-fase5c-validacao-supervisionada-seletores.md](docs/48-fase5c-validacao-supervisionada-seletores.md) | FASE 5C-H: Coleta Manual de Seletores |
| [docs/51-fase5d-simulacao-operacional.md](docs/51-fase5d-simulacao-operacional.md) | FASE 5D-S: Simulação Operacional Ponta a Ponta |
| [docs/52-referencias-github-sei.md](docs/52-referencias-github-sei.md) | Estudo de repositórios GitHub do SEI e aprendizados aplicáveis |
| [docs/53-camada-ia-claude.md](docs/53-camada-ia-claude.md) | Camada de IA com Claude (papéis lógicos, guard como barreira) |
| [docs/54-guia-rapido-operacao.md](docs/54-guia-rapido-operacao.md) | Guia rápido: como usar o Agente 19 com o SEI (passo a passo) |

## Estrutura-alvo

```text
agente-sei-inteligente/
├── README.md
├── .env.example
├── docs/
├── app/
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

O usuario humano continua no controle. O agente pode ler, resumir, classificar, sugerir providencia e gerar minuta. Atos oficiais no SEI permanecem manuais: assinatura, envio, tramitacao, conclusao, ciencia, cancelamento, exclusao e liberacao de acesso externo ficam fora do agente.
