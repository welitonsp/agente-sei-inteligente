# Regras operacionais do Manual do SEI (base curada para RAG)

Base de conhecimento curada a partir da leitura do Manual do Usuario SEI 4.0+/PEN
(ver `docs/17-leitura-manuais-sei.md`). Contem apenas **regras resumidas e
citacoes**, nunca o texto integral do manual. Uso: consulta e raciocinio do
Agente 19. `execucao=false`. Conhecimento nunca vira permissao — o
`sei_action_guard` continua sendo a barreira final.

## Processo e documento sao entidades diferentes
No SEI, o processo concentra documentos, historico, unidades envolvidas,
restricoes de acesso e prazos. Todo documento existe dentro de um processo. Ao
resumir ou classificar, trate processo e documento como entidades distintas.
Fonte: Manual do Usuario SEI (gestao por processo).

## Niveis de acesso: publico, restrito e sigiloso
O acesso a um processo/documento pode ser publico, restrito ou sigiloso. O agente
deve preservar e sinalizar o nivel de acesso, nunca rebaixar sigilo. Acesso
restrito ou sigiloso exige hipotese legal. Fonte: Manual do Usuario SEI
(restricao de acesso).

## Minuta e rascunho ate a assinatura
Antes da assinatura, o documento produzido no editor do SEI e tratado como
minuta. Minuta pode ser criada, editada e salva; nao e ato oficial. O Agente 19
pode preparar/gerar minuta, mas a assinatura transforma minuta em ato e e sempre
humana. Fonte: Manual do Usuario SEI (minuta e assinatura).

## Ciencia nao equivale a assinatura
Dar ciencia indica que o usuario verificou um processo ou documento, mas nao
equivale a assinar. O agente nao deve dar ciencia automatica. Fonte: Manual do
Usuario SEI (ciencia).

## Tipo documental deve ser existente
Ao sugerir um documento, o agente deve escolher um tipo documental que ja existe
no SEI (despacho, oficio, informacao, encaminhamento, memorando etc.). Nunca
criar um novo tipo de documento no cadastro administrativo. Fonte: Manual do
Usuario SEI (incluir documento; tipos/series).

## Controle de prazos e retorno programado
O SEI possui controle de prazos e retorno programado, com indicacoes de
vencimento. O agente deve identificar prazos e retornos programados como eventos
de controle e sinalizar para acompanhamento humano. Fonte: Manual do Usuario SEI
(controle de prazos).

## Historico e andamento sao contexto, nao decisao
O historico registra modificacoes e andamentos. O agente pode usar historico e
andamento como fonte de contexto, mas nunca como decisao final. Fonte: Manual do
Usuario SEI (historico).

## Documentos internos e externos
Documentos formais devem preferencialmente ser produzidos no editor do SEI
(internos). Documentos externos sao anexados. O agente diferencia a origem ao
analisar. Fonte: Manual do Usuario SEI (documentos internos e externos).

## Acesso externo e concessao controlada
O acesso externo permite que interessados vejam o processo por periodo
determinado. Liberar acesso externo e ato controlado e NUNCA deve ser
automatizado pelo agente. Fonte: Manual do Usuario SEI (acesso externo).

## Lista de perigo: atos que exigem humano
Mesmo existindo no SEI, estes atos NUNCA devem ser executados automaticamente
pelo agente e servem como lista de perigo (onde o agente para): assinar
documento, enviar processo, tramitar processo, concluir processo, dar ciencia,
excluir documento, excluir processo, cancelar documento, reabrir processo,
sobrestar processo, alterar sigilo/acesso, liberar acesso externo, enviar e-mail
pelo SEI. Fonte: `docs/17` e Manual SEI (operacoes sensiveis como lista de perigo).

## WebServices: escopo minimo e read-only
O SEI expõe WebServices, mas a integracao exige cadastro previo e escopo minimo.
Para o agente, apenas operacoes de consulta/listagem sao referencia
(consultarDocumento, consultarProcedimento, listarAndamentos, listarUnidades,
listarHipotesesLegais). Operacoes de escrita (incluirDocumento, lancarAndamento,
enviarProcesso, excluirDocumento) ficam bloqueadas sem autorizacao formal. Fonte:
Manual SEI WebServices v4.0 (ver `docs/17`).
