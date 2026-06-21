# Alertas no celular

## Objetivo

Garantir que eventos, prazos e pendencias importantes cheguem rapidamente aos responsaveis por meio de canal movel.

## Canal inicial

O MVP deve usar Telegram, por ser simples, barato e adequado para alertas operacionais.

Variaveis:

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Canais suportados

| Canal | Fase | Observacao |
| --- | --- | --- |
| Telegram | MVP | Canal principal de alerta no celular |
| E-mail | MVP | Copia formal ou fallback |
| Google Agenda | MVP | Convite e lembretes nativos |
| WhatsApp | Futuro | Depende de viabilidade tecnica, custo e autorizacao |

## Tipos de alerta

| Tipo | Quando enviar |
| --- | --- |
| Evento criado | Ao criar evento na agenda |
| Prazo detectado | Ao detectar prazo em documento ou e-mail |
| Minuta pronta | Quando rascunho estiver disponivel para revisao |
| Acao bloqueada | Quando o agente tentar ou receber comando proibido |
| Erro tecnico | Quando houver falha de API, e-mail, PDF ou agenda |
| Pendencia humana | Quando faltar dado essencial |

## Modelo de mensagem

```text
[Agente SEI - 19 CRPM]
Tipo:
Assunto:
Origem:
Data/Horario:
Local:
Providencia:
Status:
Link/Painel:
```

## Severidade

| Nivel | Uso |
| --- | --- |
| Informativo | Evento criado, resumo disponivel |
| Atencao | Prazo novo, dados incompletos, revisao pendente |
| Urgente | Prazo curto, falha relevante, acao bloqueada |

## Regras

1. Nao enviar documento completo por alerta.
2. Nao expor dados sensiveis desnecessarios.
3. Sempre registrar o envio.
4. Registrar erro quando o alerta falhar.
5. Evitar alertas duplicados para a mesma demanda.
6. Permitir silencioso ou agrupamento em horarios definidos, se a rotina exigir.

## Status de notificacao

| Status | Significado |
| --- | --- |
| Pendente | Notificacao criada, ainda nao enviada |
| Enviada | Canal confirmou envio |
| Falhou | Houve erro tecnico |
| Reenviada | Nova tentativa executada |
| Cancelada | Notificacao nao deve mais ser enviada |

