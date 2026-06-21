# Leitura dos manuais SEI

Data da leitura: 2026-06-21

Fontes locais lidas:

1. `d:\MEUS DOCUMENTOS\Downloads\manual_do_usuario_sei2.pdf`
2. `d:\MEUS DOCUMENTOS\Downloads\SEI-WebServices-v4.0.pdf`

## Manual do Usuario SEI

Arquivo: `manual_do_usuario_sei2.pdf`  
Versao identificada no PDF: 2.5.1  
Paginas: 149

### Aprendizados principais

O SEI trabalha com gestao por processo. Todo documento deve estar dentro de um processo, e o processo concentra documentos, historico, unidades envolvidas, restricoes de acesso, prazos e operacoes.

Topicos relevantes para o agente:

1. Tela Controle de Processos: mostra processos abertos na unidade, recebidos ou gerados.
2. Tela do Processo: exibe arvore de documentos, andamento, processos relacionados e operacoes possiveis.
3. Restricao de acesso: existem niveis publico, restrito e sigiloso.
4. Controle de prazos: o SEI possui retorno programado e indicacoes de vencimento.
5. Ciencia: indica que usuario verificou processo ou documento, mas nao equivale a assinatura.
6. Historico: registra modificacoes e andamentos do processo.
7. Documentos internos e externos: documentos formais devem preferencialmente ser produzidos no editor do SEI.
8. Minuta: antes da assinatura, documento produzido no sistema e tratado como minuta.
9. Assinatura: pode ser feita por login/senha ou token, e transforma minuta em ato assinado.
10. Acesso externo: permite acesso de interessados por periodo determinado.

### Impacto na arquitetura do agente

O manual deve alimentar a base de conhecimento operacional do agente. Ele ajuda a IA a responder perguntas como:

1. O que significa processo aberto na unidade?
2. Qual a diferenca entre minuta, documento assinado e documento externo?
3. Quando uma demanda tem prazo?
4. O que e retorno programado?
5. O que e ciencia?
6. Quais campos devem ser considerados ao resumir processo ou documento?
7. Quais atos exigem humano?

### Regras operacionais extraidas

1. O agente deve tratar processo e documento como entidades diferentes.
2. O agente deve preservar nivel de acesso e sinalizar restricao.
3. O agente deve diferenciar ciencia, assinatura, envio e conclusao.
4. O agente deve considerar minuta como rascunho ate revisao/assinatura humana.
5. O agente deve usar historico e andamento como fonte de contexto, nao como decisao final.
6. O agente deve identificar retorno programado e prazos externos como eventos de controle.

### Acoes que continuam proibidas para automacao

Mesmo existindo no SEI, estas acoes nao devem ser executadas automaticamente:

1. Enviar processo.
2. Concluir processo.
3. Excluir processo.
4. Excluir documento.
5. Cancelar documento.
6. Assinar documento.
7. Dar ciencia automatica.
8. Liberar acesso externo.
9. Alterar sigilo ou restricao.

## Manual SEI WebServices

Arquivo: `SEI-WebServices-v4.0.pdf`  
Paginas: 55

### Aprendizados principais

O SEI possui interface de WebServices para integracao com sistemas externos. O acesso exige cadastro previo do sistema cliente no SEI, associacao de servicos e operacoes permitidas, alem de autenticacao por chave de acesso ou configuracao equivalente.

O documento informa que algumas operacoes podem ser restringidas por unidade, tipo de processo ou tipo de documento. Isso confirma que a integracao tecnica deve ser feita com escopo minimo.

### Operacoes observadas

Operacoes de consulta/listagem:

```text
consultarBloco
consultarDocumento
consultarProcedimento
consultarProcedimentoIndividual
consultarPublicacao
listarAndamentos
listarAndamentosMarcadores
listarCargos
listarCidades
listarContatos
listarEstados
listarExtensoesPermitidas
listarFeriados
listarHipotesesLegais
listarMarcadoresUnidade
listarPaises
listarSeries
listarTiposConferencia
listarTiposProcedimento
listarUnidades
listarUsuarios
```

Operacoes de escrita ou alteracao:

```text
atribuirProcesso
anexarProcesso
bloquearProcesso
definirControlePrazo
definirMarcador
desanexarProcesso
desbloquearProcesso
disponibilizarBloco
enviarEmail
enviarProcesso
excluirBloco
excluirDocumento
excluirProcesso
gerarBloco
gerarProcedimento
incluirDocumento
incluirDocumentoBloco
incluirProcessoBloco
lancarAndamento
reabrirProcesso
registrarOuvidoria
relacionarProcesso
removerControlePrazo
removerRelacionamentoProcesso
removerSobrestamentoProcesso
sobrestarProcesso
```

### Classificacao para o projeto

Permitidas na primeira fase SEI:

```text
consultarDocumento
consultarProcedimento
consultarProcedimentoIndividual
listarAndamentos
listarUnidades
listarUsuarios
listarTiposProcedimento
listarSeries
listarHipotesesLegais
```

Bloqueadas ate autorizacao formal especifica:

```text
definirControlePrazo
definirMarcador
lancarAndamento
gerarBloco
incluirDocumento
```

Essas operacoes existem tecnicamente no WebServices, mas nao devem ser implementadas no agente por padrao. Para qualquer excecao futura, exigir autorizacao formal do orgao gestor do SEI, justificativa administrativa, testes de auditoria e revisao do `guardiao-seguranca-sei`.

Proibidas para o agente autonomo:

```text
enviarProcesso
excluirDocumento
excluirProcesso
reabrirProcesso
sobrestarProcesso
anexarProcesso
desanexarProcesso
bloquearProcesso
desbloquearProcesso
disponibilizarBloco
enviarEmail
registrarOuvidoria
removerControlePrazo
removerRelacionamentoProcesso
removerSobrestamentoProcesso
```

## Conclusao tecnica

Os manuais devem ser usados de duas formas:

1. Como base de conhecimento do agente para orientar respostas, classificacoes e minutas.
2. Como fonte para regras de seguranca, especialmente separando leitura, preparacao e atos oficiais.

O `manual_do_usuario_sei2.pdf` pode entrar integralmente em uma base RAG. O `SEI-WebServices-v4.0.pdf` tambem pode entrar, mas com metadados de risco, para impedir que a IA recomende ou execute operacoes sensiveis sem o guarda de permissoes.

No estado atual do projeto, WebServices deve ser tratado como referencia tecnica controlada e nao como plano de implementacao de escrita no SEI.
