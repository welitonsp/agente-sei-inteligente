# Modelo de dados

## Banco inicial

Para comecar sem custo, usar SQLite.

Depois, se necessario, migrar para PostgreSQL.

## Entidades minimas

```text
processes
documents
emails
events
drafts
notifications
audit_logs
settings
```

## processes

Representa processo SEI ou controle administrativo equivalente.

Campos sugeridos:

```text
id
sei_number
subject
origin
status
created_at
updated_at
```

## documents

Representa documento extraido de e-mail, PDF, texto manual ou SEI.

Campos sugeridos:

```text
id
process_id
source_type
source_reference
title
text_hash
extracted_text_path
summary
classification
confidence
created_at
updated_at
```

## emails

Representa mensagem processada.

Campos sugeridos:

```text
id
message_id
sender
recipients
subject
received_at
processed_at
status
has_attachments
raw_reference
created_at
updated_at
```

## events

Representa evento ou prazo enviado para agenda.

Campos sugeridos:

```text
id
process_id
document_id
title
event_type
start_at
end_at
location
description
deduplication_key
google_event_id
status
created_at
updated_at
```

## drafts

Representa minuta gerada pelo agente.

Campos sugeridos:

```text
id
process_id
document_id
draft_type
content
status
reviewed_by
reviewed_at
created_at
updated_at
```

## notifications

Representa alerta enviado.

Campos sugeridos:

```text
id
related_type
related_id
channel
recipient
message
severity
status
sent_at
error_message
created_at
updated_at
```

## audit_logs

Representa trilha de auditoria.

Campos sugeridos:

```text
id
actor_type
actor_id
action
target_type
target_id
result
reason
metadata
created_at
```

## settings

Representa configuracoes editaveis.

Campos sugeridos:

```text
id
key
value
description
updated_by
updated_at
```

## Chaves de duplicidade

Eventos:

```text
processo + titulo + data + horario + local
```

E-mails:

```text
message_id
```

Documentos:

```text
source_reference + text_hash
```

## Retencao

Configuracao inicial:

```text
AUDIT_LOG_RETENTION_DAYS=365
```

Essa retencao deve ser confirmada pela chefia do projeto, considerando rotina administrativa, auditoria e protecao de dados.

