# Fase 40 - Knowledge base local do 19 CRPM

Data: 2026-06-22
Status: PROTOTIPO_IMPLEMENTADO_SEM_DADOS_REAIS

## Objetivo

Criar a estrutura local, gratuita e auditavel para alimentar o Agente 19 com
regras reais do 19 CRPM, sem usar IA paga e sem inventar unidade responsavel.

## Escopo implementado

- [x] Pasta `knowledge_base/fluxos_19crpm/`.
- [x] Template `unidades_19crpm.csv`.
- [x] Template `unidades_alto_comando.csv`.
- [x] Template `palavras_chave_19crpm.csv`.
- [x] Template `regras_direcionamento.csv`.
- [x] Template `modelos_resposta.md`.
- [x] Carregador local em `app/intelligence/knowledge_base.py`.
- [x] Triagem/roteamento local em `app/intelligence/local_triage.py`.
- [x] Endpoint `POST /api/triage-local`.
- [x] Botao `Triagem local` no painel.
- [x] Botao `Triagem local` no desktop.
- [x] Testes automatizados.

## Regra principal

Se nao houver regra real clara, o sistema deve retornar:

```text
interesse_19crpm = indefinido
unidade_sugerida = ""
revisao_humana_obrigatoria = true
```

O sistema nao deve inventar unidade, fundamento, autoridade, prioridade ou
providencia.

## Arquivos da base local

### `unidades_19crpm.csv`

```csv
codigo,nome,tipo,ativo,observacao
```

### `palavras_chave_19crpm.csv`

```csv
termo,categoria,peso,interesse,ativo,observacao
```

### `regras_direcionamento.csv`

```csv
id,termos,unidade_destino,tipo_minuta,providencia,interesse,prioridade,confianca,ativo,observacao
```

O campo `termos` aceita multiplos termos separados por ponto e virgula.

## Fluxo

1. Usuario analisa texto/PDF.
2. Usuario clica em `Triagem local`.
3. O sistema consulta a knowledge base local.
4. Se houver regra valida, sugere unidade, tipo de minuta e providencia.
5. Se nao houver regra, retorna indefinido e exige revisao.
6. A sugestao pode preencher campos para o minutador, mas nao executa ato no SEI.

## Pendencias

- [ ] Preencher unidades reais do 19 CRPM.
- [ ] Preencher unidades de Alto Comando relevantes.
- [ ] Preencher palavras-chave reais.
- [ ] Preencher regras reais de direcionamento.
- [ ] Revisar dados com responsavel do projeto.
- [ ] Homologar com pelo menos 5 casos anonimizados.

## Como testar

```bat
.venv\Scripts\python.exe scripts\check_no_secrets.py .
.venv\Scripts\python.exe -m pytest
```
