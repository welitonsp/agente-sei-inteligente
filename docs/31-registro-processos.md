# Registro de processos

Este documento registra processos internos do projeto.

## Formato

```text
ID:
Nome:
Objetivo:
Entrada:
Saida:
Responsavel:
Ferramentas:
Evidencias:
Criterio de aceite:
Bloqueios:
Status:
```

## PROC-0001

Nome: Desenvolvimento da fundacao tecnica  
Objetivo: Criar estrutura segura minima para iniciar o sistema.  
Entrada: Documentacao, matriz de conformidade e checklist de desenvolvimento.  
Saida: `app/`, permissoes, guardiao, banco, logs e testes.  
Responsavel: Engenharia do projeto.  
Ferramentas: Python, FastAPI, SQLite, pytest, GitHub Actions.  
Evidencias: Testes passando, commit, PR e logs de CI.  
Criterio de aceite: Acoes proibidas bloqueadas por teste automatizado.  
Bloqueios: Nenhuma integracao externa antes do guardiao.  
Status: CONCLUIDO. Evidencia: 84 testes passando (TEST-0004), guardiao em `app/sei/sei_action_guard.py`, workflow CI em `.github/workflows/ci.yml` e GitHub Actions aprovado no PR #1.

## PROC-0002

Nome: Analise MVP por texto/PDF  
Objetivo: Permitir que servidor cole texto ou envie PDF para analise sem acesso automatico ao SEI.  
Entrada: Numero do processo, texto copiado ou PDF baixado pelo servidor.  
Saida: Resumo, prazo, evento, unidade sugerida ou revisao humana obrigatoria.  
Responsavel: Engenharia do projeto.  
Ferramentas: Painel web, extrator PDF, skills administrativas.  
Evidencias: Resultado estruturado, log e teste com exemplo anonimizado.  
Criterio de aceite: Nao pesquisar/navegar/clicar no SEI.  
Bloqueios: Dados reais sem autorizacao; unidade sem regra real.  
Status: NAO_INICIADO.

## PROC-0003

Nome: Controle de mudancas com IA  
Objetivo: Garantir que codigo gerado com IA seja revisado, testado e rastreavel.  
Entrada: Alteracao proposta.  
Saida: Commit/PR com declaracao de uso de IA, testes e revisao.  
Responsavel: Autor do PR e revisor.  
Ferramentas: Git, GitHub, CI, testes.  
Evidencias: PR, checks, review e merge.  
Criterio de aceite: CI verde e ausencia de segredos/dados reais.  
Bloqueios: Falha em teste de seguranca.  
Status: APROVADO.

## PROC-0004

Nome: Configuracao de credenciais OAuth do Google  
Objetivo: Habilitar Calendar (escrita) e People (leitura) com menor privilegio, sem guardar senha.  
Entrada: Projeto no Google Cloud, APIs Calendar e People ativadas, credencial Desktop app.  
Saida: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `GOOGLE_REFRESH_TOKEN` no `.env` local.  
Responsavel: Chefe do projeto (consentimento) e Engenharia (codigo).  
Ferramentas: `scripts/google_oauth_setup.py`, `scripts/google_validate.py`, escopos `calendar.events` e `contacts.readonly`.  
Evidencias: Saida do `google_validate.py` (contagens, sem segredos).  
Criterio de aceite: Validacao read-only confirma acesso a agenda e contagem de Oficiais; nenhum segredo versionado.  
Bloqueios: Sem credenciais completas, permanece em dry-run.  
Status: EM_ANDAMENTO. Client ID configurado; secret e refresh token pendentes.

## PROC-0005

Nome: Agenda dos Oficiais com deduplicacao  
Objetivo: Preparar/criar evento dos Oficiais sem duplicar com o calendario real.  
Entrada: Evento (titulo, data, hora, local), processo SEI, convidados resolvidos (marcador OFICIAIS).  
Saida: Evento simulado (dry-run) ou criado (real), ou bloqueio por duplicidade (`status=duplicate`).  
Responsavel: Engenharia do projeto.  
Ferramentas: `agenda_service`, `calendar_backend`, `contacts_resolver`, `ics_reader`, `runtime`.  
Evidencias: Testes de agenda/contatos/ICS e auditoria com contagem de convidados.  
Criterio de aceite: Guard exige aprovacao humana; dedup local e por ICS funcionam; e-mails nao aparecem em log.  
Bloqueios: Convite real apenas com backend real; criar evento sem convidado e bloqueado.  
Status: CONCLUIDO em dry-run; criacao real depende de PROC-0004.

## PROC-0006

Nome: CI/CD e gate de qualidade  
Objetivo: Impedir regressao de seguranca e versionamento acidental de segredos.  
Entrada: Branch com codigo de aplicacao, testes automatizados e regras de Git/IA.  
Saida: Workflow GitHub Actions executando teste e varredura de segredos.  
Responsavel: Engenharia do projeto.  
Ferramentas: `.github/workflows/ci.yml`, `pytest`, `scripts/check_no_secrets.py`.  
Evidencias: `check_no_secrets.py` OK e 84 testes passando localmente (TEST-0004).  
Criterio de aceite: PR falha se testes ou gate de segredos falharem; branch `main` protegida antes do merge.  
Bloqueios: Protecao de branch ainda precisa ser configurada no GitHub.  
Status: EM_ANDAMENTO. Workflow e scanner criados; validacao local aprovada; GitHub Actions aprovado no PR #1.
