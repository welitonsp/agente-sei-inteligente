# FASE 5 - Minuta controlada no SEI

## Objetivo

Definir a arquitetura segura para o Agente 19 preparar criacao de minuta no SEI sem transformar o agente em usuario autonomo do sistema.

O projeto continua particular/local, sem API oficial, sem WSSEI, sem modulo oficial SEI IA e sem autorizacao institucional de automacao. O usuario faz login manualmente no SEI Goias e qualquer uso real depende de homologacao previa.

## Premissas obrigatorias

1. O usuario faz login manualmente no SEI.
2. O agente nao guarda senha.
3. O agente nao captura cookie, token ou sessao.
4. A sessao Playwright deve ser efemera.
5. O perfil do navegador nao deve ser persistido.
6. O LLM nao controla o navegador.
7. O LLM apenas analisa texto, classifica, sugere providencia e gera conteudo.
8. Qualquer interacao com SEI deve ser codigo deterministico, auditado, com allow-list e default-deny.

## FASE 5A - arquitetura segura simulada

Status: implementada como desenho/contrato seguro e simulacao. PATCH 4 de hardening aplicado. Nao ha escrita real no SEI.

Componentes do desenho aprovado:

1. `MinutaWriter` centraliza qualquer tentativa de minuta.
2. Token de confirmacao amarrado a processo + tipo de documento + hash do texto.
3. Verificacao de processo correto antes de qualquer tentativa de escrita.
4. Allow-list separada para escrita controlada.
5. Stubs `NotImplementedError` para a UI real.
6. `ENABLE_MINUTA_CREATION=false` por padrao.
7. Auditoria registra metadados e `text_hash`, nunca texto integral.

O aceite da FASE 5A e provar que o fluxo bloqueia escrita acidental, nao captura credenciais e nao permite atos oficiais.

## FASE 5B-Homologacao

Status: preparada, sem escrita real.

A FASE 5B-homologacao cria os contratos que precisam estar preenchidos antes de qualquer escrita real:

1. Cadastro da minuta em `app/sei/minuta_cadastro.py`.
2. Manifesto de seletores em `app/sei/selector_manifest.py`.
3. Avaliador de prontidao em `app/sei/fase5b_homologacao.py` (modulo estritamente para homologacao futura, nao producao).
4. Diagnostico da API em `app/sei/api_discovery.py` (ferramenta para diagnostico local/nao-destrutivo, sem integracao oficial).
5. Template de seletores em `knowledge_base/sei_homologacao/minuta_selectors.template.json`.

Regras de cadastro:

1. `tipo_documento` deve ser um tipo ja existente no SEI.
2. `nivel_acesso` e obrigatorio.
3. Acesso restrito ou sigiloso exige `hipotese_legal`.
4. `descricao`, `interessado` e `destinatario` podem ser exigidos conforme o tipo documental.
5. `text_hash` e obrigatorio para amarrar o cadastro ao texto revisado.

Regras de seletores:

1. Todos os seletores minimos devem estar preenchidos.
2. Todos os seletores minimos devem estar com status `homologado`.
3. Seletores relacionados a assinar, tramitar, enviar, concluir, ciencia, cancelar, excluir ou liberar acesso externo sao bloqueados.
4. O template versionado nao contem seletores reais.
5. Mesmo com cadastro e seletores validos, `real_write_allowed=false`.

## FASE 5B - futura escrita real

A FASE 5B so pode ser iniciada depois de homologacao dos seletores reais e autorizacao explicita para teste controlado.

Fluxo permitido:

1. Criar uma minuta usando um tipo de documento ja existente no SEI.
2. Selecionar o tipo de documento.
3. Preencher cadastro.
4. Inserir texto no editor.
5. Salvar minuta.
6. Parar.

## Limites permanentes

Mesmo em FASE 5B, o agente nunca deve:

1. Assinar documento.
2. Tramitar processo.
3. Enviar processo.
4. Concluir processo.
5. Dar ciencia.
6. Cancelar documento.
7. Excluir documento.
8. Liberar acesso externo.
9. Enviar e-mail pelo SEI.
10. Criar tipo de documento no cadastro administrativo do SEI.

## Feature flags

```env
ENABLE_SEI_BROWSER_AUTOMATION=false
ENABLE_MINUTA_CREATION=false
MINUTA_TOKEN_SECRET=dev-insecure-trocar-em-producao
LOG_FULL_TEXT=false
```

Regras:

1. `ENABLE_MINUTA_CREATION=false` e o padrao seguro.
2. `MINUTA_TOKEN_SECRET` padrao deve ser bloqueado em `APP_ENV=prod`.
3. `LOG_FULL_TEXT=false` deve ser mantido para dados reais.
4. Escrita real deve permanecer como `NotImplementedError` enquanto a FASE 5B nao estiver homologada.

## PATCH 4 - hardening final

Status: executado.

1. `MINUTA_TOKEN_SECRET` padrao bloqueado em `APP_ENV=prod`.
2. `ENABLE_MINUTA_CREATION=true` bloqueado em producao enquanto FASE 5B nao estiver homologada.
3. `MinutaWriter` audita `text_hash`, nunca texto integral.
4. Teste arquitetural criado contra uso direto de Playwright fora dos arquivos permitidos.
5. Escrita real mantida como `NotImplementedError`.

## Proximo passo

FASE 5B futura: homologar seletores reais, exigir nivel de acesso explicitamente,
validar tipo de documento ja existente e parar apos salvar a minuta.
