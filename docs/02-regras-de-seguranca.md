# Regras de seguranca

## Principio central

O agente prepara, mas nao decide. Atos oficiais continuam sob responsabilidade humana.

O projeto e particular/local. O usuario faz login manualmente no SEI Goias e o
agente nao deve solicitar, receber, armazenar, registrar, interceptar ou
processar usuario, senha, cookie, token, sessao, `localStorage`,
`sessionStorage` ou headers de autenticacao.

O LLM nao controla o navegador. O LLM pode analisar texto, classificar, sugerir
providencia e gerar conteudo. Qualquer interacao com a tela do SEI deve ser
feita por codigo deterministico, auditado e protegido por allow-list/default-deny.

## Acoes permitidas

As acoes permitidas devem ser centralizadas em `app/core/permissions.py` quando a implementacao comecar:

```text
LER_PROCESSO
LER_DOCUMENTO
RESUMIR
CLASSIFICAR
IDENTIFICAR_PRAZO
IDENTIFICAR_EVENTO
CRIAR_EVENTO_AGENDA
ADICIONAR_CONVIDADOS_AGENDA
ENVIAR_CONVITE_AGENDA
ENVIAR_ALERTA
GERAR_MINUTA
SALVAR_MINUTA
REGISTRAR_LOG
```

## Acoes proibidas

Estas acoes devem ser bloqueadas em qualquer modulo, especialmente na automacao web do SEI:

```text
ASSINAR_DOCUMENTO
ENVIAR_PROCESSO
TRAMITAR_PROCESSO
CONCLUIR_PROCESSO
CANCELAR_DOCUMENTO
EXCLUIR_DOCUMENTO
DAR_CIENCIA_AUTOMATICA
CONCEDER_CREDENCIAL
LIBERAR_ACESSO_EXTERNO
ALTERAR_SIGILO_AUTOMATICAMENTE
```

## Guarda obrigatorio do SEI

Toda rotina do modulo SEI deve passar por `app/sei/sei_action_guard.py`.

O guarda deve:

1. Receber a acao pretendida.
2. Validar se a acao e permitida.
3. Bloquear a acao proibida antes de qualquer clique, chamada ou automacao.
4. Registrar log da tentativa.
5. Exigir aprovacao humana quando a acao for sensivel, mesmo que permitida.

## Automacao web

Se o projeto usar Playwright, Selenium ou ferramenta similar, ela deve operar com lista positiva de acoes. Isso significa que o agente so pode fazer o que estiver explicitamente autorizado.

Controles recomendados:

1. Bloquear seletores relacionados a assinar, enviar, concluir, cancelar, excluir, ciencia e tramitacao.
2. Rodar automacao SEI em modo assistido.
3. Exigir usuario autenticado manualmente.
4. Nao armazenar senha do SEI.
5. Registrar URL, processo, documento, acao e resultado.
6. Tirar captura de tela apenas se houver politica institucional autorizando.
7. Usar sessao Playwright efemera.
8. Nao persistir perfil de navegador.
9. Passar toda leitura por chokepoint.
10. Usar `ReadOnlyPage` para impedir escrita em rotas de leitura.

## FASE 5 - Minuta controlada

### FASE 5A - simulada

A FASE 5A valida a arquitetura de escrita controlada sem escrever no SEI.

Requisitos:

1. `MinutaWriter` como ponto unico para tentativa de minuta.
2. Token de confirmacao amarrado a processo + tipo de documento + hash do texto.
3. Verificacao do processo certo antes de qualquer escrita.
4. Allow-list separada para escrita controlada.
5. Stubs `NotImplementedError` para UI real.
6. `ENABLE_MINUTA_CREATION=false` por padrao.
7. Auditoria sem texto integral.

### FASE 5B - futura

Somente com homologacao, a FASE 5B podera criar uma minuta usando um tipo de
documento ja existente no SEI, preencher cadastro, inserir texto no editor,
salvar a minuta e parar.

Mesmo na FASE 5B, permanecem proibidos assinatura, tramitacao, envio,
conclusao, ciencia, cancelamento, exclusao, liberacao de acesso externo,
envio de e-mail pelo SEI e criacao de tipo de documento no cadastro
administrativo do SEI.

## Segredos

Nao devem entrar no repositorio:

1. Senha do SEI.
2. Senha de e-mail.
3. Token do Telegram.
4. Credenciais Google.
5. Chaves de API de IA.
6. Dados pessoais ou documentos reais usados como teste.

Use `.env` local e mantenha apenas `.env.example` versionado.

## Dados sensiveis

O sistema pode lidar com informacoes administrativas sensiveis. Por isso:

1. Logs nao devem armazenar documento completo quando nao for necessario.
2. Resumos devem ser suficientes para operacao, nao copias integrais sem controle.
3. Acesso ao painel web deve exigir autenticacao.
4. Exportacoes devem ser controladas.
5. Retencao de logs deve ser definida pela chefia do projeto.

## Auditoria minima

Cada acao relevante deve registrar:

1. Data e hora.
2. Usuario ou processo automatico.
3. Origem da demanda.
4. Acao solicitada.
5. Resultado.
6. Motivo de bloqueio, quando houver.
7. ID externo, quando houver agenda ou notificacao.

## Politica de confianca da IA

As respostas da IA devem ser tratadas como sugestoes. Quando houver baixa confianca, ambiguidade ou conflito de datas, o item deve ir para revisao humana.

Exemplos que exigem revisao:

1. Mais de uma data possivel.
2. Horario ausente.
3. Evento sem local definido.
4. Prazo com redacao ambigua.
5. Documento com possivel urgencia institucional.
6. Minuta que mencione decisao, sancao, autorizacao ou responsabilizacao.
