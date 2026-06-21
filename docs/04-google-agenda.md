# Google Agenda

## Objetivo

Usar o Google Agenda como canal oficial de organizacao de eventos, prazos e compromissos administrativos do 19 CRPM.

## Agenda padrao

```text
SEI 19 CRPM - Oficiais
```

O ID da agenda deve ficar em variavel de ambiente:

```text
GOOGLE_CALENDAR_ID=
```

## Grupo de convidados

O grupo de Oficiais deve ser configurado no `.env`:

```text
OFFICERS_GROUP_EMAIL=
```

O sistema deve adicionar esse grupo automaticamente nos eventos confirmados.

## Titulo do evento

Ordem de preferencia:

1. Nome oficial do evento.
2. Nome da reuniao.
3. Nome do curso.
4. Nome da solenidade.
5. Assunto principal do documento.

Padrao recomendado:

```text
[Tipo] Nome do evento - Unidade/Origem
```

Exemplos:

```text
[Reuniao] Alinhamento operacional - 19 CRPM
[Curso] Capacitacao SEI - PMGO
[Prazo] Resposta ao Oficio 123/2026
```

## Campo observacao

O campo de observacao deve seguir o modelo:

```text
Processo SEI:
Origem:
Assunto:
Resumo:
Providencia:
Data:
Horario:
Local:
Responsavel:
Observacao:
```

## Lembretes

Padrao inicial:

| Tipo | Lembretes |
| --- | --- |
| Evento comum | 1 dia antes e 1 hora antes |
| Curso ou solenidade | 3 dias antes, 1 dia antes e 1 hora antes |
| Prazo administrativo | 7 dias antes, 3 dias antes, 1 dia antes e no dia |
| Prazo urgente | Imediato, 1 dia antes e no dia |

## Controle de duplicidade

Cada evento deve gerar uma chave unica:

```text
processo + titulo + data + horario + local
```

Antes de criar evento, o sistema deve:

1. Calcular a chave.
2. Verificar se ja existe evento com a mesma chave.
3. Atualizar ou vincular ao existente, se necessario.
4. Registrar log da decisao.

## Confirmacao humana

Durante homologacao, todos os eventos devem passar por revisao. Depois, eventos com alta confianca poderao ser criados automaticamente, desde que:

1. Data esteja clara.
2. Horario esteja claro.
3. Local esteja claro ou seja marcado como "a definir".
4. Titulo esteja coerente.
5. Nao haja duplicidade.
6. Origem esteja registrada.

## Falhas

| Falha | Acao |
| --- | --- |
| Sem data | Nao criar evento; abrir pendencia |
| Sem horario | Aplicar regra definida ou pedir revisao |
| Sem local | Permitir "local a definir" apenas com revisao |
| Grupo de convidados vazio | Criar pendencia tecnica |
| Erro de API | Registrar erro e tentar novamente |

