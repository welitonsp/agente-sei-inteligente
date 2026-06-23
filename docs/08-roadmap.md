# Roadmap

## Premissa atual

O Agente SEI Inteligente Particular e uma solucao local supervisionada. O usuario faz login manualmente no SEI Goias e o agente nao usa API oficial, WSSEI, modulo SEI IA ou credencial institucional especial.

O LLM nao controla o navegador. O LLM analisa texto, classifica, sugere providencia e gera conteudo. Qualquer interacao com SEI deve ser feita por codigo deterministico, auditado e protegido por allow-list/default-deny.

## FASE 1 - Fundacao documental e governanca

Status: concluida.

Resultado:

1. README.
2. Documentacao de arquitetura.
3. Regras de seguranca.
4. Politica de dados.
5. Politica de identidade/sessao SEI.
6. Registro de decisoes.
7. Checklist de desenvolvimento.

## FASE 2 - Fundacao tecnica local

Status: concluida.

Resultado:

1. Estrutura `app/`.
2. Configuracao local.
3. Banco SQLite.
4. Logger/auditoria.
5. Permissoes.
6. Guarda de acoes.
7. Scanner de segredos.
8. CI com testes.

## FASE 3 - Intake local e apoio administrativo

Status: prototipo implementado.

Resultado:

1. Texto colado manualmente.
2. PDF pesquisavel.
3. Painel local.
4. Agente 19 Desktop.
5. Minutador local fora do SEI.
6. Knowledge base local 19 CRPM.
7. Agenda em dry-run.

## FASE 4 - Leitura/anÃ¡lise supervisionada

Status: em desenvolvimento.

Objetivo: permitir leitura supervisionada do processo aberto pelo usuario no SEI, sem capturar credenciais e sem praticar atos oficiais.

Resultado esperado:

1. Sessao com login manual do usuario.
2. Sessao Playwright efemera.
3. Chokepoint de leitura.
4. `ReadOnlyPage` para bloquear escrita por desenho.
5. Confirmacao do numero do processo.
6. Leitura da arvore de documentos.
7. Leitura de conteudo visivel.
8. Resumo, classificacao, prazos e providencia sugerida.
9. Auditoria sem texto integral.

## FASE 5A - Minuta controlada simulada

Status: arquitetura segura simulada implementada com PATCH 4.

Objetivo: preparar a arquitetura de criacao de minuta sem escrever no SEI.

Resultado esperado:

1. `MinutaWriter` como ponto unico de escrita controlada.
2. Token de confirmacao amarrado a processo + tipo de documento + hash do texto.
3. Verificacao do processo correto antes de qualquer escrita.
4. Allow-list separada para escrita controlada.
5. Stubs `NotImplementedError` para UI real.
6. `ENABLE_MINUTA_CREATION=false` por padrao.
7. Nenhuma escrita real no SEI.
8. Startup com `assert_safe_environment()`.
9. Auditoria por `text_hash`, nunca texto integral.
10. Teste arquitetural contra uso direto de Playwright fora do arquivo permitido.

## FASE 5B-homologacao

Status: preparada sem escrita real.

Objetivo: validar cadastro, nivel de acesso e seletores antes de qualquer escrita real.

Resultado:

1. Contrato de cadastro da minuta.
2. Nivel de acesso obrigatorio.
3. Hipotese legal para acesso restrito/sigiloso.
4. Manifesto de seletores homologaveis.
5. Bloqueio de seletores de atos oficiais.
6. `real_write_allowed=false`.

## FASE 5B - Escrita real de minuta futura

Status: nao iniciada.

Objetivo: criar uma minuta usando um tipo de documento ja existente no SEI, somente depois de homologacao dos seletores reais.

Fluxo maximo permitido:

1. Criar minuta real no SEI.
2. Selecionar tipo de documento ja existente.
3. Preencher cadastro.
4. Inserir texto no editor.
5. Salvar minuta.
6. Parar.

Nunca permitido:

1. Assinar.
2. Tramitar.
3. Enviar.
4. Concluir.
5. Dar ciencia.
6. Cancelar.
7. Excluir.
8. Liberar acesso externo.

## FASE 6 - Agenda/notificacoes

Status: futura/continuidade.

Objetivo: consolidar agenda e notificacoes com custo zero ou recursos gratuitos ja autorizados.

Resultado esperado:

1. Agenda real apenas com credenciais configuradas localmente.
2. Convites com revisao humana.
3. Alertas sem documento completo.
4. Deduplicacao.
5. Auditoria.

## FASE 7 - Hardening/auditoria final

Status: futura.

Objetivo: revisar riscos restantes apos a FASE 5B de homologacao.

Resultado esperado:

1. Revisao final das acoes proibidas.
2. Evidencias de homologacao da FASE 5B.
3. Revisao de logs e auditoria.
4. Revisao de politica de instalacao/uso.
5. Revisao de testes de regressao de seguranca.
Resultado:

1. Bot Telegram.
2. Mensagens padronizadas.
3. Status de envio.
4. Reenvio em falha.
5. Logs de notificacao.

## Etapa 5 - Leitura de e-mail

Resultado:

1. Conexao com e-mail institucional.
2. Leitura de caixa de entrada.
3. Extracao de corpo e anexos.
4. Marcacao como processado.
5. Evitar reprocessamento.

## Etapa 6 - Leitura de PDF

Resultado:

1. Extracao de texto.
2. Identificacao de PDF sem texto.
3. Resumo.
4. Extracao de data, horario e local.
5. Registro do documento.

## Etapa 7 - Inteligencia administrativa

Resultado:

1. Classificador.
2. Extrator de eventos.
3. Extrator de prazos.
4. Sugeridor de providencia.
5. Gerador de minuta.
6. Indicador de confianca.

## Etapa 8 - Interface web

Resultado:

1. Painel de demandas.
2. Fila de revisao.
3. Visualizacao de agenda.
4. Editor de minuta.
5. Logs.
6. Configuracoes.

## Etapa 9 - SEI read-only

Resultado:

1. Abertura manual do SEI pelo servidor.
2. Uso da sessao ja autenticada na estacao do servidor.
3. Leitura assistida somente da pagina atual ou documento selecionado.
4. Resumo.
5. Sem senha armazenada.
6. Sem usuario unico.
7. Sem atos oficiais.

## Etapa 10 - Minutador SEI assistido

Resultado:

1. Gerar minuta fora do SEI.
2. Exibir texto para revisao humana.
3. Permitir copia manual pelo servidor.
4. Bloquear assinatura e envio.
5. Registrar auditoria interna do agente.

Observacao: a criacao de minuta (escrita automatica dentro do SEI) exige confirmacao humana previa. O Agente 19 preenche a minuta mas o humano revisa, corrige, assina e tramita manualmente.

## Etapa 11 - Operacao v1

Resultado:

1. Agente funcional em rotina real controlada.
2. Agenda.
3. Celular.
4. E-mail.
5. PDF.
6. Minutas.
7. Logs.
8. Seguranca.

## Etapa 12 - FASE 38: Agente SEI RPA Assistido (NÃºmero de Processo)

Resultado:

1. O servidor aciona o Agente 19 por uma janela/logo flutuante, informando o nÃºmero do processo.
2. O Agente abre o processo e exporta para PDF usando a sessÃ£o ativa do usuÃ¡rio, sem capturar token ou senha.
3. AnÃ¡lise integral do processo identificando metadados essenciais.
4. Pergunta proativa sobre criaÃ§Ã£o de minuta (OfÃ­cio, Despacho, etc.).
5. CriaÃ§Ã£o da minuta (apÃ³s confirmaÃ§Ã£o), preenchimento sem assinatura e aviso de prontidÃ£o.

## Etapa 13 - FASE 39: MemÃ³ria Institucional e Aprendizado Supervisionado

Resultado:

1. O Agente 19 registra e mantÃ©m o histÃ³rico institucional de decisÃµes e minutas (MemÃ³ria Institucional).
2. O Agente aprende supervisionadamente com as correÃ§Ãµes de texto feitas pelos humanos durante a revisÃ£o.
3. Melhoria contÃ­nua e segura nas sugestÃµes de providÃªncias e classificaÃ§Ãµes.

