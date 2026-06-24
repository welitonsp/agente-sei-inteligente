# Camada de IA — Claude no controle (papéis lógicos)

Implementa a decisão de projeto: **Claude (Anthropic) como provedor de IA
padrão**, dentro de uma abstração configurável por `AI_PROVIDER`. O desenho
segue o padrão LiteLLM observado no `anatelgovbr/sei-ia` (ver
[docs/52](52-referencias-github-sei.md)): o código chama um **papel lógico**,
não um modelo concreto.

## Papéis lógicos
Arquivo: `app/intelligence/ai_provider.py`.

| Papel | Ação SEI (guard) | Modelo | max_tokens | effort | thinking |
|---|---|---|---|---|---|
| `RESUMO` | `RESUMIR` | claude-opus-4-8 | 1024 | low | — |
| `CLASSIFICACAO` | `CLASSIFICAR` | claude-opus-4-8 | 512 | low | — |
| `TRIAGEM` | `CLASSIFICAR` | claude-opus-4-8 | 512 | low | — |
| `MINUTA` | `GERAR_MINUTA` | claude-opus-4-8 | 4096 | high | adaptive |

Trocar de modelo/provedor é **configuração** (`AI_PROVIDER`, `AI_MODEL`), não
alteração de código.

## Barreira final: o guard, nunca o prompt
Antes de **qualquer** chamada de IA, o papel é mapeado para a ação SEI
correspondente e submetido ao guard (`app/sei/sei_action_guard.evaluate`). Se a
ação não for permitida, levanta `PermissionError` **sem** chamar a rede. O
prompt nunca é a barreira de segurança — o guard é.

## Provedores
- **`ClaudeProvider`** — SDK oficial `anthropic` (import tardio). Requer
  `ANTHROPIC_API_KEY` (segredo, só no `.env` local). Usa adaptive thinking e
  `output_config.effort` por papel. O SDK já reexecuta 429/5xx com backoff e
  **não** reexecuta erro de autenticação — a política desejada; configuramos só
  `max_retries`.
- **`EchoProvider`** — offline e determinístico (testes e custo zero). Não
  acessa rede nem depende do SDK, mas **respeita o guard** igualmente.

## Configuração (`.env` local)
```
AI_PROVIDER=claude          # ou: echo (offline)
AI_MODEL=                   # opcional: sobrescreve o modelo de todos os papéis
ANTHROPIC_API_KEY=sk-ant-…  # SEGREDO; nunca versionar
```

## Uso
```python
from app.intelligence.ai_provider import AIRole, get_ai_provider

provider = get_ai_provider()                  # padrão: Claude
r = provider.complete(AIRole.RESUMO, texto, system="Resuma de forma fiel.")
print(r.text, r.model, r.usage)
```

## Segurança
- Credencial só no `.env` local; o `check_no_secrets` continua valendo.
- A camada de IA **gera e sugere**; não pratica atos oficiais. Escrita de minuta
  no SEI permanece bloqueada (`ENABLE_MINUTA_CREATION=false`) e fora desta
  camada.
- Não envia texto integral a logs; auditoria continua por hash/sanitização.

## Próximos passos
Ligar os papéis ao pipeline existente: `RESUMO`/`CLASSIFICACAO` reforçando o
`institutional_analyzer` quando uma análise mais rica for desejada, e `MINUTA`
alimentando o `MinutaWriter` (que continua gated), sempre com revisão humana.
