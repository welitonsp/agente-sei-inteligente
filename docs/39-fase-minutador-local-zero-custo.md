# Fase 39 - Minutador local zero custo

Data: 2026-06-22
Status: PROTOTIPO_IMPLEMENTADO

## Objetivo

Gerar rascunhos administrativos sem IA paga, sem API externa e sem escrita no
SEI. O usuario analisa texto/PDF no Agente 19, gera uma minuta local e copia o
resultado para revisao humana.

## Escopo implementado

- [x] Motor local em `app/intelligence/local_minutador.py`.
- [x] Templates locais em `knowledge_base/templates_minutas/`.
- [x] Tipos de minuta: despacho, oficio, informacao e encaminhamento.
- [x] Classificacao por regras simples.
- [x] Endpoint local `POST /api/generate-draft`.
- [x] Botao `Gerar minuta local` no painel web local.
- [x] Botao `Gerar minuta` no Agente 19 Desktop.
- [x] Resultado copiavel.
- [x] Alertas de revisao humana obrigatoria.
- [x] Acoes oficiais bloqueadas no contrato.
- [x] Auditoria sem persistir texto integral.
- [x] Testes automatizados.

## Fluxo permitido

1. Usuario abre o SEI manualmente.
2. Usuario copia texto ou exporta PDF manualmente.
3. Agente 19 analisa texto/PDF.
4. Usuario clica em gerar minuta.
5. O minutador escolhe tipo provavel por regras ou respeita tipo escolhido.
6. O sistema gera rascunho local.
7. Usuario revisa, ajusta e copia manualmente.
8. Qualquer criacao/assinatura/tramitacao no SEI continua manual.

## Tipos suportados

| Tipo | Uso sugerido |
| --- | --- |
| `despacho` | Encaminhamento interno para providencias nos autos |
| `oficio` | Resposta formal externa ou comunicacao oficial revisada |
| `informacao` | Registro informativo para subsidiar decisao |
| `encaminhamento` | Envio a unidade/responsavel para conhecimento e providencias |

## Regras de seguranca

- [x] Nao usa IA paga.
- [x] Nao chama API externa.
- [x] Nao escreve no SEI.
- [x] Nao cria documento oficial.
- [x] Nao salva minuta como documento oficial.
- [x] Nao assina.
- [x] Nao tramita.
- [x] Nao envia processo.
- [x] Nao conclui processo.
- [x] Mantem revisao humana obrigatoria.

## Campos pendentes

Quando faltar informacao, o texto mantem marcadores como:

```text
[PREENCHER processo SEI]
[PREENCHER assunto]
[PREENCHER unidade/responsavel]
[PREENCHER destinatario]
[PREENCHER prazo/evento, se aplicavel]
```

## Limitacoes conhecidas

1. Classificacao ainda e por regras simples.
2. Unidade responsavel real depende da knowledge base do 19 CRPM.
3. Fundamentos legais nao sao inventados.
4. OCR real ainda nao foi implementado.
5. Criacao automatica de minuta dentro do SEI continua fora do escopo ate
   homologacao/autorizacao institucional.

## Como testar

```bat
.venv\Scripts\python.exe scripts\check_no_secrets.py .
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m app.desktop
```

