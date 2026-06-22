# Agentes de IA - Funcionário Digital de IA (Agente 19)

## Objetivo

Organizar a IA em agentes especializados sob a visão-mestre do Agente 19, o Funcionário Digital de IA do 19º CRPM. O Agente 19 é a face unificada que coordena responsabilidades claras, preparando, sugerindo, organizando, criando minutas e aprendendo.

## Principio

A IA nao deve executar ferramentas livremente. Ela deve produzir uma intencao estruturada, que passa por validacao, guarda de acoes, regras de negocio e logs.

## Agente classificador

Entrada:

1. Texto extraido.
2. Origem.
3. Metadados.

Saida:

```text
tipo:
assunto:
origem:
prioridade:
providencia_sugerida:
confianca:
justificativa:
```

Tipos iniciais:

1. Evento.
2. Prazo.
3. Oficio.
4. Despacho.
5. Convocacao.
6. Curso.
7. Reuniao.
8. Solenidade.
9. Documento informativo.
10. Demanda sem classificacao.

## Agente de eventos

Entrada: texto e classificacao.

Saida:

```text
titulo:
data:
horario_inicio:
horario_fim:
local:
participantes:
responsavel:
observacao:
confianca:
campos_pendentes:
```

Regra: se data ou horario forem ambiguos, nao criar evento automaticamente.

## Agente de prazos

Entrada: texto e classificacao.

Saida:

```text
prazo:
tipo_prazo:
data_limite:
responsavel:
providencia:
risco:
confianca:
```

## Agente resumidor

Entrada: texto extraido.

Saida:

```text
resumo_curto:
resumo_operacional:
pontos_de_atencao:
providencia_sugerida:
```

O resumo deve ser fiel ao documento. Quando nao houver informacao, deve declarar ausencia em vez de inventar.

## Agente minutador

Entrada:

1. Documento de origem.
2. Tipo de minuta.
3. Resumo.
4. Campos administrativos.

Saida:

```text
tipo_minuta:
texto:
campos_usados:
alertas:
confianca:
```

Proibicao: o minutador nao pode simular assinatura, decisao final ou envio oficial.

## Agente agenda

Entrada:

1. Evento extraido.
2. Configuracao do calendario.
3. Grupo de Oficiais.

Saida:

```text
acao_solicitada:
evento:
chave_duplicidade:
precisa_revisao:
```

O agente agenda so executa criacao quando o guarda permitir e as regras minimas estiverem satisfeitas.

## Agente notificador

Entrada:

1. Evento, prazo, erro ou pendencia.
2. Canal.
3. Destinatario.

Saida:

```text
mensagem:
canal:
destinatario:
severidade:
```

## Agente SEI

Entrada:

1. Processo selecionado.
2. Documento selecionado.
3. Sessao autenticada pelo usuario.

Saida:

```text
texto_lido:
resumo:
providencia_sugerida:
minuta_opcional:
acoes_bloqueadas:
```

O agente SEI deve ser tratado como o modulo mais sensivel do sistema.

## Agente Triador 19 CRPM

Entrada:

1. Numero do processo SEI.
2. Lista de documentos acessiveis na sessao do servidor.
3. Texto extraido dos documentos.
4. Tabela de unidades do 19 CRPM.
5. Tabela de unidades de Alto Comando consideradas relevantes.
6. Regras internas de direcionamento.

Saida:

```text
processo:
documentos_lidos:
documentos_relevantes_19crpm:
documentos_descartados:
assunto:
finalidade:
prazo:
risco:
unidade_origem:
unidade_destino_sugerida:
justificativa_destino:
providencia_sugerida:
minuta_sugerida:
confianca:
campos_pendentes:
```

Regras:

1. Nao inventar unidade responsavel.
2. Se houver duvida entre duas unidades, enviar para revisao humana.
3. Preservar origem, processo, documento e prazo.
4. Indicar quais documentos embasaram a sugestao.
5. Nao sugerir envio automatico no SEI.

## Formato de resposta dos agentes

Sempre que possivel, respostas devem ser estruturadas em JSON ou objeto equivalente. Texto livre deve ser usado apenas para minutas, resumos e mensagens ao usuario.

## Avaliacao de confianca

Escala recomendada:

| Valor | Significado |
| --- | --- |
| 0.90 a 1.00 | Alta confianca |
| 0.70 a 0.89 | Revisao recomendada |
| 0.00 a 0.69 | Revisao obrigatoria |

## Base de conhecimento

A pasta `knowledge_base/` deve armazenar:

1. Manual do SEI.
2. Modelos PMGO.
3. Fluxos do 19 CRPM.
4. Prompts aprovados.
5. Exemplos anonimizados.

## Testes dos agentes

Cada agente deve ter testes com documentos anonimizados:

1. Evento claro.
2. Evento com data ambigua.
3. Prazo claro.
4. Documento sem prazo.
5. PDF com texto ruim.
6. Minuta com campos incompletos.
7. Tentativa de acao proibida.
