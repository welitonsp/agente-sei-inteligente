# FASE 58-64 - Control Plane de Missoes Supervisionadas

Data: 2026-07-08

## Objetivo

Evoluir o Agente 19 de um conjunto de ferramentas assistivas para uma
plataforma de missoes administrativas supervisionadas. A nova arquitetura segue
o principio: **workflow manda, agente assessora, humano decide e pratica ato
oficial**.

O Control Plane nao amplia liberdade operacional no SEI. Ele amplia capacidade
de coordenar varias tarefas junto ao usuario, mantendo:

1. leitura e analise supervisionadas;
2. propostas estruturadas antes de qualquer acao;
3. guard central antes de ferramenta;
4. aprovacao humana quando houver efeito externo;
5. auditoria sanitizada;
6. bloqueio permanente de atos oficiais do SEI.

## Inspiracao arquitetural

A arquitetura adota padroes comuns em agentes modernos:

- workflows explicitos para etapas previsiveis;
- agentes especializados para analise, triagem, minuta, prazo, agenda e alerta;
- tool registry com escopo de permissao;
- ActionProposal antes de execucao;
- Human-in-the-loop para qualquer efeito externo;
- tracing e auditoria sem texto integral;
- evaluation harness com casos anonimizados.

## Contratos centrais

Implementado em:

```text
app/agent/control_plane.py
```

Modelos:

| Modelo | Funcao |
| --- | --- |
| `Mission` | Pacote operacional da demanda do usuario |
| `MissionStep` | Etapa individual da missao |
| `AgentRun` | Execucao logica de um agente especializado |
| `ToolCall` | Chamada de ferramenta com risco e guard |
| `ActionProposal` | Proposta estruturada antes de executar |
| `ApprovalRequest` | Pedido de aprovacao humana |
| `AuditEvent` | Evento de auditoria sanitizada |
| `DecisionRecord` | Decisao final do guard/control plane |

## Estados canonicos

```text
draft
running
needs_human_input
ready_for_review
approved
executed
blocked
failed
cancelled
```

## Tool Registry

Cada ferramenta deve declarar:

```text
name
description
risk_level
read_only
requires_human_approval
writes_external_system
writes_sei
allowed_actions
```

Ferramentas iniciais:

| Ferramenta | Risco | Efeito externo | Escreve SEI | Regra |
| --- | --- | --- | --- | --- |
| `mission_control` | low | nao | nao | analise, triagem e minuta local |
| `calendar_agent` | medium | sim | nao | exige aprovacao humana |
| `notification_agent` | medium | sim | nao | exige aprovacao humana |

## Guard central

Fluxo obrigatorio:

```text
ActionProposal
  -> evaluate_action_proposal()
  -> app.sei.sei_action_guard.evaluate()
  -> DecisionRecord
```

Regras:

1. ferramenta desconhecida: bloqueada;
2. acao fora do escopo da ferramenta: bloqueada;
3. acao proibida do SEI: bloqueio duro;
4. acao sensivel/externa sem aprovacao: `precisa_revisao`;
5. acao permitida e aprovada: `approved`.

## Mission Queue - proxima entrega

A fila de missoes deve persistir somente dados sanitizados:

```text
mission_id
status
titulo_resumido
processo_sei
origem
created_at
updated_at
risk_level
campos_pendentes
etapa_recomendada
```

Visoes desejadas no painel:

1. Missoes pendentes.
2. Missoes em analise.
3. Missoes prontas para revisao.
4. Missoes com prazo critico.
5. Missoes bloqueadas por seguranca.
6. Missoes concluidas.

## Approval Center - proxima entrega

Toda aprovacao deve mostrar ao usuario:

1. o que sera feito;
2. onde sera feito;
3. qual ferramenta sera usada;
4. se ha efeito externo;
5. se escreve no SEI;
6. qual risco existe;
7. qual conteudo/hash foi aprovado;
8. quem aprovou;
9. quando aprovou;
10. qual acao continua bloqueada.

## Memoria operacional sanitizada

Pode persistir:

- `mission_id`;
- tipo provavel;
- status;
- prazos extraidos;
- unidade sugerida;
- decisoes humanas;
- hash de conteudo aprovado.

Nao pode persistir por padrao:

- texto integral do processo;
- senha;
- cookie;
- token;
- sessao;
- localStorage;
- sessionStorage;
- headers de autenticacao.

## Evaluation Harness

Conjunto minimo recomendado:

```text
10 casos simples
10 casos com prazo
10 casos com minuta
10 casos com risco de sigilo/LGPD
10 casos com agenda/notificacao
```

Metricas:

| Metrica | Meta |
| --- | --- |
| Acerto de classificacao | >= 90% |
| Extracao de prazo | >= 95% |
| Acao SEI proibida | 0 ocorrencias |
| Persistencia de senha/cookie/token | 0 ocorrencias |
| Minutas com revisao humana | 100% |
| Logs sem texto integral | 100% |

## Criterios de aceite da fundacao P0

1. `ActionProposal` existe antes de qualquer acao externa.
2. Tool Registry nega ferramenta desconhecida.
3. Guard central bloqueia atos oficiais.
4. Agenda/alerta exigem aprovacao humana.
5. Nenhuma ferramenta declara `writes_sei=true`.
6. Contrato de missao inclui `mission_id` e pacote `control_plane`.
7. Testes cobrem bloqueio, aprovacao e sanitizacao.
8. README descreve o Control Plane de Missoes Supervisionadas.

## Limite operacional permanente

O Agente 19 pode coordenar tarefas, mas nao vira usuario autônomo do SEI.
Assinatura, envio, tramitacao, conclusao, ciencia, cancelamento, exclusao e
liberacao de acesso externo permanecem manuais e sob responsabilidade humana.
