# Skills especialistas do Agente SEI

## Objetivo

Dividir o Agente SEI em competencias especializadas. Cada skill deve ter funcao clara, entrada definida, saida estruturada, limites de seguranca e criterio de revisao humana.

O agente principal sera um orquestrador. Ele nao deve tentar resolver tudo sozinho; ele chama a skill certa conforme a tarefa.

## Principio de desenho

```text
Robo SEI / Painel Web
        |
        v
Orquestrador
        |
        v
Skills especialistas
        |
        v
Resultado revisavel pelo servidor
```

Nenhuma skill pode assinar, enviar, tramitar, concluir, dar ciencia, excluir, cancelar, alterar sigilo ou usar senha do SEI.

## Lista inicial de skills

| Skill | Funcao |
| --- | --- |
| `sei-leitor-readonly` | Ler pagina, processo ou documento acessivel na sessao do servidor |
| `triagem-19crpm` | Decidir se o processo/documento interessa ao 19 CRPM |
| `roteador-unidades-19crpm` | Sugerir qual unidade do 19 CRPM deve tratar a demanda |
| `extrator-prazos` | Identificar prazo, risco e lembretes |
| `extrator-eventos` | Identificar evento, data, horario, local e participantes |
| `resumidor-administrativo` | Explicar conteudo em linguagem clara e operacional |
| `minutador-administrativo` | Gerar minuta fora do SEI para revisao humana |
| `agenda-oficiais` | Preparar/criar evento no Google Agenda |
| `alerta-celular` | Enviar alerta via Telegram/e-mail |
| `guardiao-seguranca-sei` | Bloquear acao proibida e exigir revisao |
| `auditor-processos` | Registrar logs, fontes usadas, decisoes e bloqueios |
| `rag-manual-sei` | Consultar manual SEI, WebServices, modelos e regras internas |

## Skill `sei-leitor-readonly`

Finalidade:

1. Ler somente conteudo acessivel na sessao ativa do servidor.
2. Extrair arvore de documentos, metadados e texto.
3. Entregar material para as demais skills.

Entrada:

```text
processo_sei
pagina_atual
html_ou_texto_visivel
usuario_local
```

Saida:

```text
processo
documentos
metadados
texto_extraido
erros_leitura
```

Limites:

1. Nao faz login.
2. Nao digita senha.
3. Nao clica em botoes sensiveis.
4. Nao altera nada no SEI.

## Skill `triagem-19crpm`

Finalidade:

1. Verificar se o processo interessa ao 19 CRPM.
2. Separar documentos relevantes dos irrelevantes.
3. Explicar por que o item interessa ou nao interessa.

Fontes:

1. Unidades do 19 CRPM.
2. Unidades de Alto Comando relevantes.
3. Palavras-chave e assuntos internos.
4. Conteudo dos documentos.

Saida:

```text
interesse_19crpm:
tipo_interesse:
documentos_relevantes:
documentos_ignorados:
justificativa:
confianca:
```

## Skill `roteador-unidades-19crpm`

Finalidade:

Sugerir qual unidade pertencente ao 19 CRPM deve receber a providencia.

Entrada:

```text
assunto
finalidade
origem
local
tipo_demanda
regras_direcionamento
```

Saida:

```text
unidade_sugerida:
motivo:
alternativas:
precisa_revisao:
```

Regra: se nao houver regra clara, marcar `precisa_revisao=true`.

## Skill `extrator-prazos`

Finalidade:

Identificar se ha prazo e classificar o risco operacional.

Saida:

```text
ha_prazo:
data_limite:
hora_limite:
tipo_prazo:
risco:
fonte_do_prazo:
lembretes_sugeridos:
```

## Skill `extrator-eventos`

Finalidade:

Identificar cursos, reunioes, solenidades, convocacoes, agendas e compromissos.

Saida:

```text
ha_evento:
titulo:
data:
horario_inicio:
horario_fim:
local:
publico_alvo:
fonte:
agenda_sugerida:
```

## Skill `resumidor-administrativo`

Finalidade:

Explicar o conteudo do processo/documento em linguagem clara, curta e orientada a providencia.

Formato:

```text
Resumo:
Finalidade:
Origem:
O que o 19 CRPM precisa fazer:
Prazo:
Risco:
Documentos que embasam:
```

## Skill `minutador-administrativo`

Finalidade:

Gerar minuta fora do SEI para revisao humana.

Tipos iniciais:

1. Despacho de encaminhamento.
2. Oficio de resposta.
3. Comunicacao interna.
4. Registro de providencia.
5. Convocacao ou ciencia de evento.

Limite: nunca simular assinatura, decisao final ou envio oficial.

## Skill `agenda-oficiais`

Finalidade:

Preparar e criar evento no Google Agenda quando houver data, horario e assunto suficientes.

Regras:

1. Evitar duplicidade.
2. Adicionar grupo de Oficiais.
3. Preencher observacao padronizada.
4. Registrar ID do evento.

## Skill `alerta-celular`

Finalidade:

Enviar alerta no celular sobre prazo, evento, minuta pronta, erro ou acao bloqueada.

Regra: alerta nao deve conter documento completo nem dado sensivel desnecessario.

## Skill `guardiao-seguranca-sei`

Finalidade:

Validar qualquer intencao de acao antes de executar ferramenta externa.

Bloquear:

```text
ASSINAR_DOCUMENTO
ENVIAR_PROCESSO
TRAMITAR_PROCESSO
CONCLUIR_PROCESSO
DAR_CIENCIA_AUTOMATICA
EXCLUIR_DOCUMENTO
CANCELAR_DOCUMENTO
ALTERAR_SIGILO_AUTOMATICAMENTE
LIBERAR_ACESSO_EXTERNO
CONCEDER_CREDENCIAL
```

## Skill `auditor-processos`

Finalidade:

Registrar:

1. Quem solicitou analise.
2. Qual processo foi analisado.
3. Quais documentos foram usados.
4. Quais skills foram chamadas.
5. Qual resultado foi entregue.
6. Se houve revisao humana.
7. Se alguma acao foi bloqueada.

## Skill `rag-manual-sei`

Finalidade:

Consultar a biblioteca de conhecimento:

1. Manual do Usuario SEI.
2. WebServices SEI.
3. Modelos PMGO.
4. Fluxos do 19 CRPM.
5. Prompts aprovados.

Uso:

1. Explicar procedimento.
2. Tirar duvida operacional.
3. Embasar classificacao.
4. Evitar resposta inventada.

## Ordem recomendada no fluxo do robozinho

```text
sei-leitor-readonly
        |
        v
rag-manual-sei
        |
        v
resumidor-administrativo
        |
        v
triagem-19crpm
        |
        v
extrator-prazos + extrator-eventos
        |
        v
roteador-unidades-19crpm
        |
        v
minutador-administrativo
        |
        v
agenda-oficiais / alerta-celular
        |
        v
auditor-processos
```

