# Como preencher a knowledge base do 19 CRPM

Este é o **gargalo nº1 do projeto** (ver `docs/64-plano-de-sucesso.md`). Enquanto
estes arquivos não tiverem dados reais, a triagem retorna `indefinido` e não
sugere unidade — de propósito, para nunca inventar.

Você **não precisa** saber CSV. Abra cada arquivo no Excel/LibreOffice ou me
passe os dados em texto solto que eu formato. Todos os arquivos usam vírgula como
separador e codificação UTF-8.

## Regra do `ativo`

Cada linha tem uma coluna `ativo`. Linhas com `ativo=false` são **ignoradas**
pelo sistema. Por isso os arquivos já vêm com linhas de **EXEMPLO** inertes
(`ativo=false`): copie uma, troque pelos dados reais e mude para `ativo=true`.
Assim nada quebra enquanto você preenche aos poucos.

## Os 4 arquivos

### 1. `unidades_19crpm.csv` — as unidades da sua região
| coluna | o que é | exemplo |
| --- | --- | --- |
| `codigo` | sigla curta única | `36BPM` |
| `nome` | nome como aparece nos processos | `PM/36 BPM` |
| `tipo` | batalhao, companhia, pelotao, comando_regional… | `batalhao` |
| `ativo` | `true` para valer | `true` |
| `observacao` | nota livre (opcional) | |

### 2. `unidades_alto_comando.csv` — órgãos de direção relevantes
Mesmas colunas. Serve para reconhecer demandas que vêm do Comando-Geral,
Estado-Maior etc.

### 3. `palavras_chave_19crpm.csv` — sinais de interesse do 19 CRPM
| coluna | o que é | exemplo |
| --- | --- | --- |
| `termo` | palavra/expressão que indica interesse | `apoio operacional` |
| `categoria` | agrupamento livre | `operacional` |
| `peso` | 1 a 10; quanto mais alto, mais forte o sinal | `8` |
| `interesse` | `direto` ou `indireto` | `direto` |
| `ativo` | `true` para valer | `true` |

### 4. `regras_direcionamento.csv` — para qual unidade vai a providência
Esta é a mais importante. Cada linha diz: *"se o texto tiver estes termos,
sugira esta unidade e este tipo de minuta"*.

| coluna | o que é | exemplo |
| --- | --- | --- |
| `id` | identificador único da regra | `r36_policiamento` |
| `termos` | termos que disparam a regra, separados por `;` | `policiamento;efetivo;viatura` |
| `unidade_destino` | unidade que recebe (tem que existir no arquivo 1) | `PM/36 BPM` |
| `tipo_minuta` | despacho, oficio, informacao, encaminhamento | `despacho` |
| `providencia` | o que sugerir fazer | `Verificar pertinência e preparar despacho` |
| `interesse` | `direto` ou `indireto` | `direto` |
| `prioridade` | 0–100; regra de maior prioridade vence | `80` |
| `confianca` | 0.0–1.0; sua confiança na regra | `0.75` |
| `ativo` | `true` para valer | `true` |

## Como validamos depois

Quando você preencher (ou me mandar) os dados reais + **5 casos anonimizados**
(um texto de processo real, sem dados pessoais, e a unidade correta esperada),
eu escrevo os testes de homologação. Meta de aceite: a triagem acerta unidade e
regra em pelo menos 4 dos 5 casos.
