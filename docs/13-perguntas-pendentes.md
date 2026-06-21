# Perguntas pendentes

Estas perguntas nao bloqueiam a documentacao inicial, mas precisam ser respondidas antes da implementacao completa.

## Configuracao institucional

1. Qual e o e-mail do grupo de Oficiais que deve ser colocado em `OFFICERS_GROUP_EMAIL`?
2. A agenda sera uma agenda compartilhada existente ou uma nova agenda chamada `SEI 19 CRPM - Oficiais`?
3. Quem sera o administrador da conta Google usada na integracao?
4. A conta institucional usa Gmail, Outlook/Microsoft 365 ou outro provedor IMAP?

## Canal de celular

1. O Telegram esta autorizado como canal operacional inicial?
2. O alerta sera enviado para grupo, canal ou chat individual?
3. Existe necessidade de separar alertas por tipo: prazos, eventos, minutas e erros?

## IA

1. O projeto podera usar API externa de IA ou deve priorizar modelo local?
2. Quais tipos de documentos administrativos devem ser priorizados nos testes?
3. Existem modelos oficiais de minutas da PMGO para alimentar a base de conhecimento?
4. Ha exemplos anonimizados de e-mails, PDFs e processos para teste?

## SEI

1. O perfil do usuario no SEI permite leitura dos processos necessarios?
2. O SEI exige autenticacao multifator ou certificado no fluxo usado pela unidade?
3. A preparacao de minuta dentro do SEI sera permitida na versao 1 ou somente em fase futura? Decisao atual: nao, a minuta sera gerada fora do SEI e copiada/revisada manualmente pelo servidor.
4. Ha politica interna sobre captura de tela, extracao de texto e armazenamento de resumos do SEI?
5. Quais estacoes de trabalho poderao usar o assistente local de leitura?
6. O orgao permite extensao de navegador ou automacao local apenas para leitura?

## Interface web

1. O painel sera usado apenas no computador local, em rede interna ou tambem fora da unidade?
2. Quantos usuarios precisarao acessar o painel?
3. Deve haver perfis diferentes, como operador, revisor e administrador?
4. O painel deve ser responsivo para celular desde o MVP?
5. A unidade permite instalar extensao de navegador nas estacoes de trabalho?
6. O robozinho deve aparecer apenas no dominio `sei.go.gov.br`?
7. O painel lateral pode ler o HTML da pagina atual do SEI, ou a primeira versao deve usar somente copia/cola?

## Triagem 19 CRPM

1. Quais sao exatamente as unidades pertencentes ao 19 CRPM?
2. Quais unidades de Alto Comando devem ser consideradas relevantes?
3. Quais palavras-chave, siglas, assuntos e tipos de processo indicam interesse do 19 CRPM?
4. Quais assuntos devem ser ignorados por pertencerem a outras unidades militares?
5. Qual regra define a unidade do 19 CRPM que recebera a providencia?
6. Quando o agente deve criar evento de agenda e quando deve apenas registrar pendencia?
7. O que significa "criar o arquivo" no fluxo: gerar minuta, gerar PDF, criar pasta, abrir documento no SEI ou montar processo administrativo?
8. Quem valida a sugestao de direcionamento antes de qualquer ato no SEI?

## Operacao e auditoria

1. Por quanto tempo os logs devem ser mantidos?
2. Quem revisara os logs?
3. Qual e o procedimento quando o agente bloquear uma acao?
4. Qual e o criterio para uma demanda ser considerada concluida?
