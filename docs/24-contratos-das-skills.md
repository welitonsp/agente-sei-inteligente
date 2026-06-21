# Contratos das skills

## Objetivo

Definir entradas e saidas estruturadas para que cada skill possa ser implementada, testada e auditada.

## Envelope padrao de entrada

```json
{
  "request_id": "",
  "usuario_local": "",
  "estacao": "",
  "origem": "robozinho_sei",
  "processo_sei": "",
  "documentos": [],
  "texto": "",
  "metadata": {},
  "regras": {},
  "created_at": ""
}
```

## Envelope padrao de saida

```json
{
  "request_id": "",
  "skill": "",
  "status": "ok",
  "resultado": {},
  "confianca": 0.0,
  "fontes": [],
  "campos_pendentes": [],
  "revisao_humana_obrigatoria": false,
  "acoes_sugeridas": [],
  "acoes_bloqueadas": [],
  "logs": []
}
```

## Status permitidos

```text
ok
parcial
precisa_revisao
bloqueado
erro
```

## Contrato `sei-leitor-readonly`

Entrada minima:

```json
{
  "processo_sei": "",
  "modo_leitura": "texto_colado",
  "pagina_atual_url": "",
  "texto_visivel": "",
  "documentos_fornecidos": [],
  "usuario_local": "",
  "estacao": ""
}
```

Valores para `modo_leitura`:

```text
texto_colado
pdf_upload
pagina_atual
inventario_manual
```

Saida:

```json
{
  "processo_sei": "",
  "documentos": [
    {
      "id": "",
      "numero": "",
      "tipo": "",
      "data": "",
      "origem": "",
      "status_leitura": "lido",
      "texto_extraido": "",
      "hash_texto": ""
    }
  ],
  "documentos_nao_lidos": [],
  "avisos": [],
  "confianca": 0.0,
  "revisao_humana_obrigatoria": false
}
```

Valores para `status_leitura`:

```text
lido
parcial
nao_lido
ocr_necessario
inacessivel
ignorado_por_regra
```

## Contrato `triagem-19crpm`

Entrada minima:

```json
{
  "processo_sei": "",
  "documentos": [
    {
      "id": "",
      "tipo": "",
      "origem": "",
      "texto": ""
    }
  ],
  "regras": {
    "unidades_19crpm": [],
    "unidades_alto_comando": [],
    "palavras_chave": []
  }
}
```

Saida:

```json
{
  "interesse_19crpm": "direto",
  "nivel_prioridade": "normal",
  "documentos_relevantes": [],
  "documentos_ignorados": [],
  "justificativa": "",
  "confianca": 0.0,
  "revisao_humana_obrigatoria": true
}
```

Valores para `interesse_19crpm`:

```text
direto
indireto
informativo
nao_interessa
indefinido
```

## Contrato `roteador-unidades-19crpm`

Saida:

```json
{
  "unidade_sugerida": "",
  "motivo": "",
  "alternativas": [],
  "regra_aplicada": "",
  "confianca": 0.0,
  "revisao_humana_obrigatoria": true
}
```

## Contrato `extrator-prazos`

Saida:

```json
{
  "ha_prazo": false,
  "data_limite": null,
  "hora_limite": null,
  "tipo_prazo": "",
  "risco": "baixo",
  "texto_fonte": "",
  "lembretes_sugeridos": [],
  "confianca": 0.0
}
```

Valores para `risco`:

```text
baixo
medio
alto
urgente
```

## Contrato `extrator-eventos`

Saida:

```json
{
  "ha_evento": false,
  "titulo": "",
  "data": null,
  "horario_inicio": null,
  "horario_fim": null,
  "local": "",
  "publico_alvo": "",
  "agenda_sugerida": false,
  "campos_pendentes": [],
  "confianca": 0.0
}
```

## Contrato `resumidor-administrativo`

Saida:

```json
{
  "resumo_executivo": "",
  "finalidade": "",
  "origem": "",
  "providencia_sugerida": "",
  "pontos_de_atencao": [],
  "documentos_base": [],
  "confianca": 0.0
}
```

## Contrato `minutador-administrativo`

Entrada minima:

```json
{
  "tipo_minuta": "",
  "contexto": {},
  "modelo": "",
  "restricoes": [
    "nao_assinar",
    "nao_enviar",
    "nao_decidir_sem_base"
  ]
}
```

Saida:

```json
{
  "tipo_minuta": "",
  "texto": "",
  "campos_usados": [],
  "alertas": [],
  "revisao_humana_obrigatoria": true,
  "confianca": 0.0
}
```

## Contrato `guardiao-seguranca-sei`

Entrada:

```json
{
  "acao_solicitada": "",
  "origem": "",
  "usuario_local": "",
  "processo_sei": "",
  "justificativa": ""
}
```

Saida:

```json
{
  "permitido": false,
  "motivo": "",
  "acao": "",
  "deve_registrar_log": true
}
```

## Contrato `agenda-oficiais`

Entrada minima:

```json
{
  "evento": {
    "titulo": "",
    "data": "",
    "horario_inicio": "",
    "horario_fim": "",
    "local": "",
    "descricao": ""
  },
  "processo_sei": "",
  "documentos_base": [],
  "grupo_oficiais": "",
  "deduplication_key": "",
  "aprovado_por_humano": false
}
```

Saida:

```json
{
  "pode_criar": false,
  "precisa_revisao": true,
  "motivo": "",
  "google_event_id": "",
  "deduplication_key": "",
  "campos_pendentes": []
}
```

## Contrato `alerta-celular`

Entrada minima:

```json
{
  "tipo_alerta": "",
  "severidade": "",
  "destinatario": "",
  "mensagem": "",
  "processo_sei": "",
  "documentos_base": []
}
```

Saida:

```json
{
  "enviado": false,
  "canal": "",
  "message_id": "",
  "erro": "",
  "conteudo_reduzido": true
}
```

## Contrato `auditor-processos`

Entrada minima:

```json
{
  "request_id": "",
  "usuario_local": "",
  "estacao": "",
  "processo_sei": "",
  "skills_chamadas": [],
  "documentos_referenciados": [],
  "resultado": {},
  "acoes_bloqueadas": []
}
```

Saida:

```json
{
  "audit_log_id": "",
  "registrado": true,
  "campos_omitidos_por_seguranca": [],
  "erro": ""
}
```

## Contrato `rag-manual-sei`

Entrada minima:

```json
{
  "pergunta": "",
  "colecoes": ["manual_sei", "fluxos_19crpm"],
  "tipo_conteudo": "manual",
  "permitir_ia_externa": false
}
```

Saida:

```json
{
  "resposta": "",
  "trechos_usados": [],
  "colecoes_consultadas": [],
  "confianca": 0.0,
  "nao_encontrado": false
}
```

## Regra de validacao

Toda skill deve informar:

1. Confianca.
2. Fontes ou documentos usados.
3. Campos pendentes.
4. Se exige revisao humana.
5. Acoes sugeridas.
6. Acoes bloqueadas.

Se uma skill nao conseguir justificar a resposta, o status deve ser `precisa_revisao`.
