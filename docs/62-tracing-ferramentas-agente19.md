# FASE 62 - Tracing e ferramentas seguras do Agente 19

Data: 2026-06-29

## Objetivo

Evoluir o Agente 19 para uma arquitetura mais proxima de agentes modernos:
identidade, intencao, plano, ferramentas registradas, trace operacional e
correlacao entre agente e missao.

## Implementado

1. Registro de ferramentas seguras em `app/agent/tools.py`.
2. Tracing operacional sanitizado em `app/agent/tracing.py`.
3. `trace_id` automatico no formato `agt19-*`.
4. Resposta do agente com:
   - ferramentas disponiveis;
   - ferramentas usadas;
   - trace operacional;
   - missao correlacionada por `mission_trace_id`.
5. `mission_control` passa a devolver `mission_trace_id`.

## Principio

O trace nao salva texto integral do processo. Ele registra somente etapas,
status e detalhes operacionais de baixo risco.

## Passos de trace

```text
receber_solicitacao
detectar_intencao
montar_plano
selecionar_ferramenta
executar_ferramenta
montar_resposta
```

Quando falta contexto:

```text
verificar_contexto
```

## Ferramenta inicial

```text
mission_control
```

Caracteristicas:

1. read-only;
2. revisao humana obrigatoria;
3. analise supervisionada;
4. sem ato oficial no SEI.

## Criterios de aceite

1. Toda chamada do Agente 19 deve ter `trace.trace_id`.
2. A missao deve conter `mission_trace_id` igual ao trace do agente.
3. Ferramentas usadas devem declarar permissao e `read_only=true`.
4. Ferramenta desconhecida deve ser negada.
5. Nenhum trace deve conter texto integral do processo.
