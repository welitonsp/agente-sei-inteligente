# API e execucao de tarefas

## Objetivo

Definir como a pagina web deve solicitar tarefas ao backend e aos agentes de IA, mantendo validacao, permissao, auditoria e controle humano.

## Principio

A pagina web nao deve chamar diretamente ferramentas sensiveis. Ela cria uma solicitacao de tarefa. O backend valida, registra, chama o agente correto e so executa ferramenta externa quando a acao for permitida.

```text
Pagina web -> API -> Validador -> Agente -> Guarda de acoes -> Integracao externa -> Log
```

## Modelo de tarefa

```json
{
  "id": "task_001",
  "type": "PROCESS_EMAIL",
  "source": "web",
  "requested_by": "usuario",
  "payload": {},
  "status": "PENDING",
  "requires_human_review": false,
  "created_at": "2026-06-21T10:00:00-03:00",
  "updated_at": "2026-06-21T10:00:00-03:00"
}
```

## Status de tarefa

| Status | Significado |
| --- | --- |
| PENDING | Recebida, aguardando execucao |
| RUNNING | Em processamento |
| WAITING_REVIEW | Precisa de revisao humana |
| COMPLETED | Concluida |
| BLOCKED | Bloqueada por regra de seguranca |
| FAILED | Falha tecnica |
| CANCELED | Cancelada por usuario |

## Endpoints sugeridos

### Criar tarefa

```text
POST /api/tasks
```

Exemplo:

```json
{
  "type": "IMPORT_TEXT",
  "payload": {
    "title": "Convite para reuniao",
    "text": "conteudo colado pelo usuario"
  }
}
```

### Consultar tarefa

```text
GET /api/tasks/{task_id}
```

### Listar demandas

```text
GET /api/demands?status=WAITING_REVIEW
```

### Revisar classificacao

```text
POST /api/demands/{demand_id}/review
```

Exemplo:

```json
{
  "approved": true,
  "corrections": {
    "title": "Reuniao de alinhamento",
    "date": "2026-07-01",
    "time": "09:00",
    "location": "19 CRPM"
  }
}
```

### Criar evento de agenda

```text
POST /api/events
```

Regra: antes de chamar Google Agenda, o backend deve verificar permissao, duplicidade e campos obrigatorios.

### Gerar minuta

```text
POST /api/drafts
```

Exemplo:

```json
{
  "demand_id": "dem_001",
  "draft_type": "DESPACHO_ENCAMINHAMENTO"
}
```

### Gerar minuta local zero custo

```text
POST /api/generate-draft
```

Exemplo:

```json
{
  "assunto": "Apoio administrativo",
  "resumo": "pedido de apoio para atividade institucional",
  "processo_sei": "2026.000000",
  "tipo_minuta": "despacho",
  "unidade_destino": "PM/19 CRPM"
}
```

Regra: gera somente rascunho local copiavel. Nao cria documento no SEI, nao
assina, nao tramita, nao envia processo e exige revisao humana.

### Enviar alerta

```text
POST /api/notifications
```

### Ler documento SEI em modo assistido

```text
POST /api/sei/read-document
```

Regra: endpoint disponivel apenas quando o modulo SEI estiver habilitado e autenticado pelo usuario.

## Tipos de tarefa iniciais

```text
PROCESS_EMAIL
IMPORT_PDF
IMPORT_TEXT
CLASSIFY_DOCUMENT
EXTRACT_EVENT
EXTRACT_DEADLINE
CREATE_CALENDAR_EVENT
SEND_NOTIFICATION
GENERATE_DRAFT
READ_SEI_PROCESS
READ_SEI_DOCUMENT
```

## Tipos proibidos

Nao devem existir endpoints ou tipos de tarefa para:

```text
SIGN_SEI_DOCUMENT
SEND_SEI_PROCESS
MOVE_SEI_PROCESS
CONCLUDE_SEI_PROCESS
DELETE_SEI_DOCUMENT
GRANT_SEI_ACCESS
```

## Resposta padrao de erro

```json
{
  "error": {
    "code": "ACTION_BLOCKED",
    "message": "Acao proibida pela politica de seguranca",
    "details": {
      "action": "ASSINAR_DOCUMENTO"
    }
  }
}
```

## Resposta com revisao humana

```json
{
  "status": "WAITING_REVIEW",
  "reason": "Data ambigua no documento",
  "fields_to_review": ["date", "time"]
}
```

## Regras para a pagina web

1. Mostrar claramente quando uma tarefa esta em revisao.
2. Nao ocultar baixa confianca da IA.
3. Nao permitir acao proibida via botao, atalho ou chamada escondida.
4. Exibir historico da demanda.
5. Permitir edicao humana antes de agenda e minuta.
6. Manter o usuario informado quando uma tarefa falhar ou for bloqueada.
