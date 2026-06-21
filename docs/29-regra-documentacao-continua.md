# Regra de documentacao continua

## Objetivo

Garantir que todos os processos, decisoes, mudancas, testes, riscos e pendencias do projeto sejam documentados continuamente, evitando perda de contexto e dependencia de memoria informal.

O repositorio deve ser a fonte oficial do projeto.

## Principio

Se uma decisao muda o rumo do projeto, altera seguranca, afeta dados, muda fluxo operacional, adiciona dependencia ou libera uma etapa, ela deve ser registrada.

```text
Sem registro, nao existe como decisao oficial do projeto.
```

## O que deve ser documentado

| Tipo | Onde registrar |
| --- | --- |
| Decisao de arquitetura | `docs/30-registro-decisoes.md` |
| Mudanca de processo | `docs/31-registro-processos.md` |
| Risco novo | `docs/15-governanca-e-riscos.md` e registro especifico |
| Pendencia | `docs/13-perguntas-pendentes.md` |
| Checklist de fase | `docs/27-checklist-processos-desenvolvimento.md` |
| Mudanca de regra Git/IA | `docs/28-regras-git-ia.md` |
| Mudanca de seguranca | `docs/02-regras-de-seguranca.md` e matriz de conformidade |
| Mudanca envolvendo SEI | `docs/06`, `docs/20`, `docs/21`, `docs/22` ou `docs/25` |
| Resultado de teste/homologacao | `docs/32-registro-testes-homologacao.md` |
| Release | `docs/33-changelog.md` |

## Registro minimo obrigatorio

Cada registro deve conter:

```text
Data:
Responsavel:
Tipo:
Contexto:
Decisao ou acao:
Motivo:
Impacto:
Risco:
Arquivos afetados:
Status:
Proximo passo:
```

## Quando documentar

Documentar no mesmo PR ou commit quando:

1. Criar novo modulo.
2. Alterar regra de seguranca.
3. Alterar contrato de skill.
4. Alterar fluxo do robozinho.
5. Alterar politica de dados.
6. Criar integracao externa.
7. Adicionar dependencia.
8. Mudar banco de dados.
9. Mudar comportamento de IA.
10. Resolver pendencia importante.

## Quando nao precisa documentar em registro separado

Nao precisa registro especifico para:

1. Correcao de typo.
2. Ajuste de formatacao sem impacto.
3. Refatoracao interna sem mudar contrato.
4. Comentario de codigo sem mudanca funcional.

Mesmo nesses casos, a mensagem de commit deve ser clara.

## Regra de rastreabilidade

Toda mudanca relevante deve poder ser rastreada por:

```text
documento -> commit -> PR -> teste/evidencia -> decisao
```

Quando houver codigo, todo PR deve apontar quais documentos foram atualizados ou confirmar que nao houve impacto documental.

## Regra para conversas com IA

Quando uma decisao importante nascer em conversa com IA, ela deve ser transferida para um documento do repositorio.

Nao usar chat como fonte oficial.

Exemplos:

1. Nova decisao de arquitetura.
2. Novo risco.
3. Novo bloqueio.
4. Nova regra de seguranca.
5. Nova etapa do roadmap.
6. Mudanca em uso de IA externa.

## Regra para pendencias

Toda pendencia deve ter:

```text
ID:
Descricao:
Responsavel:
Impacto:
Bloqueia etapa:
Status:
Data de abertura:
Data de fechamento:
```

Pendencia sem responsavel deve ser tratada como pendencia do chefe do projeto.

## Regra para decisoes

Cada decisao deve ter um ID sequencial:

```text
DEC-0001
DEC-0002
DEC-0003
```

Status possiveis:

```text
PROPOSTA
APROVADA
REVOGADA
SUBSTITUIDA
EM_REVISAO
```

## Regra para processos

Cada processo interno do projeto deve ter:

1. Nome.
2. Objetivo.
3. Entrada.
4. Saida.
5. Responsavel.
6. Ferramentas.
7. Evidencias.
8. Criterio de aceite.
9. Bloqueios.

## Regra para testes e homologacao

Todo teste manual relevante deve registrar:

```text
Data:
Versao/commit:
Ambiente:
Caso testado:
Entrada usada:
Resultado esperado:
Resultado obtido:
Evidencia:
Status:
Problemas encontrados:
```

Nao registrar dados reais sensiveis em evidencias.

## Regra para changelog

Toda entrega deve atualizar `docs/33-changelog.md` com:

1. Adicionado.
2. Alterado.
3. Corrigido.
4. Segurança.
5. Riscos conhecidos.

## Templates iniciais

Os documentos abaixo devem ser usados como registros vivos:

```text
docs/30-registro-decisoes.md
docs/31-registro-processos.md
docs/32-registro-testes-homologacao.md
docs/33-changelog.md
```

## Decisao atual

A partir deste ponto, qualquer nova fase de desenvolvimento deve atualizar:

1. Checklist de processos.
2. Registro de decisoes, se houver decisao.
3. Registro de processos, se houver novo fluxo.
4. Registro de testes, se houver validacao.
5. Changelog, se houver entrega.

