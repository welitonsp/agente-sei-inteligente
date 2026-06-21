# Integracao com SEI

## URL

```text
https://sei.go.gov.br/sei/
```

## Modo de integracao

O SEI deve entrar no projeto depois de agenda, alertas, e-mail, PDF e inteligencia administrativa basica estarem funcionando.

Decisao atual: nao ha viabilidade de instalar o modulo oficial SEI IA no ambiente institucional. Portanto, a integracao sera externa/local assistida, sem modulo instalado dentro do SEI.

Modo permitido:

```text
assistido
```

Isso significa que o usuario humano abre e autentica no SEI. O agente pode apoiar leitura, resumo e preparacao de minuta, sempre dentro dos limites de seguranca.

O agente nao deve:

1. Guardar usuario.
2. Guardar senha.
3. Usar conta compartilhada.
4. Reutilizar sessao de outro servidor.
5. Executar em segundo plano no SEI.
6. Praticar atos oficiais.

## O que o agente pode fazer

1. Reconhecer tela de controle.
2. Abrir processo autorizado pelo usuario.
3. Ler arvore de documentos.
4. Ler documento selecionado.
5. Extrair texto.
6. Resumir.
7. Identificar prazo, evento e providencia.
8. Preparar minuta, se a fase do projeto permitir.
9. Salvar rascunho, se a permissao estiver habilitada.
10. Registrar log.

## O que o agente nao pode fazer

1. Assinar documento.
2. Enviar processo.
3. Tramitar processo.
4. Concluir processo.
5. Cancelar documento.
6. Excluir documento.
7. Dar ciencia automatica.
8. Conceder credencial.
9. Liberar acesso externo.
10. Alterar sigilo automaticamente.

## Automacao por pagina web

Se o agente usar uma pagina web ou navegador automatizado para executar tarefas, a automacao deve ser feita por acoes pequenas, declaradas e auditaveis.

Exemplo de ferramenta permitida:

```text
ler_texto_documento(processo, documento)
```

Exemplo de ferramenta proibida:

```text
clicar_botao_assinar()
```

## Camadas de protecao

1. Lista positiva de ferramentas permitidas.
2. Guarda central de acoes.
3. Bloqueio de seletores sensiveis.
4. Confirmacao humana para qualquer escrita.
5. Log de toda operacao.
6. Modo read-only como padrao.
7. Variavel `ALLOW_OFFICIAL_SEI_ACTIONS=false` permanente.

## Fases

### Fase 1 - Sem SEI

O agente trabalha com e-mail, PDF, agenda, Telegram e painel web.

### Fase 2 - SEI read-only

O agente le processos e documentos, resume e registra pendencias.

### Fase 3 - Minutador assistido

O agente prepara minuta ou texto auxiliar, mas para antes de qualquer ato oficial.

### Fase 4 - Operacao supervisionada

Uso real com logs, revisao humana, metricas e bloqueios testados.

## Estrategia sem modulo oficial

Sem o modulo oficial, ha duas formas seguras de aproximar o agente do SEI:

1. Importacao manual: o servidor copia texto, baixa PDF ou encaminha e-mail/documento para o agente.
2. Assistente local de leitura: o servidor abre o SEI com sua propria credencial e aciona o agente para ler somente a pagina atual, sem capturar senha ou executar cliques sensiveis.

Atos como assinar, enviar, concluir, dar ciencia, excluir, cancelar, tramitar, liberar acesso externo ou alterar sigilo continuam fora do agente.

## Criterios antes de ativar SEI

1. Permissoes implementadas e testadas.
2. Acoes proibidas bloqueadas em teste automatizado.
3. Logs funcionando.
4. Painel de auditoria disponivel.
5. Politica de uso validada pela chefia.
6. Usuario treinado para revisar e interromper automacao.
