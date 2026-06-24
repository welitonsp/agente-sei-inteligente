# Referências GitHub do SEI — Estudo e Aprendizados Aplicáveis

Estudo de repositórios públicos do **SEI (Sistema Eletrônico de Informações** —
núcleo PHP do TRF4, usado por órgãos como a PMGO) para extrair padrões aplicáveis
ao Agente 19. Foco em arquitetura, abstração de LLM e organização de testes.

> **Importante sobre licenças:** os projetos oficiais abaixo são em sua maioria
> **GPL-3.0/LGPL**. Aprendemos com os *padrões de arquitetura*, **não** copiamos
> código para dentro deste repositório sem análise de compatibilidade de licença.

## Ecossistema oficial — organização `anatelgovbr`

A ANATEL mantém os módulos oficiais do SEI em código aberto. Principais:

| Repositório | Linguagem | O que é |
|---|---|---|
| [anatelgovbr/sei-ia](https://github.com/anatelgovbr/sei-ia) | Python (GPL-3.0) | Servidor de Soluções de IA do Módulo SEI IA (desacoplado) |
| [anatelgovbr/mod-sei-ia](https://github.com/anatelgovbr/mod-sei-ia) | PHP (GPL-3.0) | Módulo de IA que integra ao core do SEI (SEI + SIP) |
| [anatelgovbr/ocr-server](https://github.com/anatelgovbr/ocr-server) | Perl (LGPL-2.1) | Servidor de OCR oficial |
| [anatelgovbr/mod-sei-pesquisa](https://github.com/anatelgovbr/mod-sei-pesquisa) | PHP | Pesquisa Pública do SEI (originalmente do CADE) |
| [anatelgovbr/mod-sei-peticionamento](https://github.com/anatelgovbr/mod-sei-peticionamento) | PHP | Peticionamento e Intimação Eletrônica |

### Arquitetura observada (sei-ia + mod-sei-ia)
- **Servidor de IA desacoplado** (Python, Docker) consumido por um **módulo PHP**
  instalado dentro do SEI. A IA nunca vive dentro do core do SEI.
- Dois submódulos de IA:
  - **SIMILARIDADE** — recomendação de processos e documentos similares (embeddings).
  - **ASSISTENTE** — IA generativa para executar *prompts* e interagir com documentos.
- Infra pesada (Docker, Airflow, requisito sugerido de 16 cores / 128 GB RAM,
  SEI v4.1.5+). É um produto institucional de grande porte — **não** é o nosso alvo.

## Aprendizados aplicáveis ao Agente 19

### 1. Abstração de LLM por aliases semânticos (LiteLLM)
O `sei-ia` usa **LiteLLM** com nomes lógicos (`standard`, `mini`, `think`,
`embedding`) que mapeiam para modelos concretos do provedor. O código chama o
papel (`think`), não o modelo (`gpt-5.2`), permitindo trocar de provedor sem
alterar a aplicação.

**Aplicar:** nossa camada `AI_PROVIDER` (decisão: **Claude como padrão**) deve
expor papéis lógicos (ex.: `resumo`, `classificacao`, `minuta`, `embedding`) e
mapeá-los para modelos Claude por configuração, mantendo a porta aberta para
outros provedores. O guard/permissões continua sendo a barreira final, nunca o
prompt.

### 2. Política de retry/reliability explícita
O LiteLLM deles define `retry_policy` por tipo de erro
(`RateLimitErrorRetries: 3`, `AuthenticationErrorRetries: 0`,
`InternalServerErrorRetries: 4`) e timeouts maiores para *reasoning models*.

**Aplicar:** ao criar o cliente Claude, configurar retries idempotentes para
rate-limit/timeout e **zero** retry para erro de autenticação; timeouts amplos
para prompts longos de minuta.

### 3. OCR como serviço dedicado
Existe um `ocr-server` oficial. Hoje nosso pipeline apenas **sinaliza**
`ocr_required` e para. Há um caminho maduro para PDFs escaneados.

**Aplicar:** evoluir o `pdf_pipeline` para integrar um OCR local (ex.: Tesseract)
sob a mesma política de sanitização/PII, em vez de só sinalizar. Manter offline e
auditável.

### 4. Organização de testes por camada
O `sei-ia` separa testes em `unit/`, `integration/`, além de `connectivity_tests`,
`env_tests`, `docker_tests`. Falham cedo em problemas de ambiente.

**Aplicar:** já temos boa cobertura unitária; vale adicionar testes de
*connectivity/env* para a futura integração de IA (ex.: validar credenciais e
disponibilidade do provedor antes de operar), sem chamar a API real nos testes.

### 5. Recurso de "similaridade" como inspiração de KB
O submódulo SIMILARIDADE (documentos/processos similares por embeddings) é uma
funcionalidade de alto valor para triagem.

**Aplicar (futuro):** sobre a `knowledge_base` local do 19 CRPM, um índice de
similaridade simples (embeddings locais) ajudaria a sugerir providências por
analogia com casos anteriores — coerente com a memória institucional supervisionada.

## O que NÃO devemos copiar
- A integração como **módulo PHP dentro do SEI** (exige instalação institucional,
  acesso a banco SEI/SIP e credencial especial) — contraria nossa premissa de
  agente local supervisionado, sem API oficial e sem credencial institucional.
- A infraestrutura pesada (Airflow, cluster). Nosso alvo é local e de custo zero.

## Resumo
O ecossistema `anatelgovbr` confirma e refina nossa direção: **IA desacoplada do
SEI**, **abstração de provedor por papéis lógicos** (Claude padrão via LiteLLM-like),
**retry/reliability explícitos** e **OCR como evolução natural** do pipeline de PDF —
sempre mantendo o guard de ações e a sanitização de PII como barreiras finais.
