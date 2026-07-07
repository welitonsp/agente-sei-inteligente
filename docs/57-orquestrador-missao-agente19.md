# FASE 57 - Orquestrador de Missao do Agente 19

Data: 2026-06-29

## Objetivo

Criar uma camada de coordenacao multiagente para transformar uma demanda em um
pacote unico de revisao humana: analise, triagem, minuta, riscos, campos
pendentes, prontidao operacional e proximo passo recomendado.

## Inovacao aplicada

O Agente 19 deixa de responder apenas por ferramentas separadas e passa a ter
um modo de "missao supervisionada". Esse modo combina:

1. Analise administrativa local/assistida.
2. Triagem e roteamento pela knowledge base do 19 CRPM.
3. Geracao de minuta local por template.
4. Calculo de prontidao operacional.
5. Plano de acao humano antes de qualquer ato oficial.

## Contrato

Entrada principal:

```text
titulo
texto
processo_sei
usuario_local
estacao
unidade_destino
tipo_minuta
```

Saida principal:

```text
status
prontidao_operacional
etapa_recomendada
plano_operacional
riscos
analise
triagem
minuta
campos_pendentes
revisao_humana_obrigatoria
acoes_bloqueadas
logs
```

## Garantias

1. Nao acessa o SEI real.
2. Nao clica, assina, envia, tramita, conclui ou da ciencia.
3. Nao substitui revisao humana.
4. Usa os guardas ja existentes do minutador e da triagem.
5. Mantem atos oficiais em `acoes_bloqueadas`.

## Uso no painel local

Endpoint:

```text
POST /api/mission-control
```

Botao:

```text
Missao Agente 19
```

O painel mostra status, prontidao operacional, etapa recomendada, unidade
sugerida, tipo de minuta, campos pendentes, riscos e plano operacional.

## Criterios de aceite

1. Demanda com texto, processo e unidade deve retornar `pronto_para_revisao`.
2. Demanda sem texto/titulo deve retornar `precisa_complemento`.
3. Unidade ausente deve aparecer como campo pendente.
4. Minuta gerada deve continuar marcada como rascunho local.
5. Acoes oficiais continuam bloqueadas.

## Proximos passos

1. Exibir a prontidao operacional no chat da extensao SEI.
2. Criar fila de missoes pendentes no painel local.
3. Homologar o orquestrador com 5 casos anonimizados do 19 CRPM.
4. Permitir exportacao de relatorio de missao em PDF local.
