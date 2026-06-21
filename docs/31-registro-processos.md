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
Status: NAO_INICIADO.

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

