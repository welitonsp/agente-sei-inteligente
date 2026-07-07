# FASE 61 - Nucleo de Agente de IA do Agente 19

Data: 2026-06-29

## Objetivo

Garantir que o produto seja explicitamente um Agente de Inteligencia Artificial,
e nao apenas um chatbot ou botao de analise.

## Definicao

O Agente 19 e um servidor digital de IA supervisionado. Ele deve:

1. perceber a demanda do usuario;
2. identificar a intencao;
3. montar plano operacional;
4. escolher ferramenta permitida;
5. executar missao supervisionada;
6. explicar resposta, riscos e pendencias;
7. manter revisao humana obrigatoria;
8. bloquear atos oficiais.

## Implementacao

Foi criado o nucleo:

```text
app/agent/agent19.py
```

Endpoint local:

```text
POST /api/agent19
```

A extensao do SEI passa a chamar o agente para a acao `19 CRPM`. O agente usa a
ferramenta segura `mission_control` para executar a analise.

## Contrato principal

Entrada:

```text
mensagem
texto
titulo
processo_sei
usuario_local
perfil_local
unidade_destino
origem
```

Saida:

```text
agente.nome
agente.tipo
agente.intencao
resposta
plano
ferramentas_usadas
resultado
revisao_humana_obrigatoria
acoes_bloqueadas
```

## Limites

Mesmo sendo agente, ele nao:

1. abre processo sozinho;
2. exporta PDF automaticamente;
3. usa senha, cookie, token, hash ou sessao;
4. clica no SEI;
5. assina, tramita, envia, conclui ou da ciencia.

## Criterio de aceite

O Agente 19 so e considerado agente quando a resposta inclui:

1. identidade do agente;
2. intencao detectada;
3. plano;
4. ferramentas usadas;
5. resultado da missao;
6. bloqueios de atos oficiais.
