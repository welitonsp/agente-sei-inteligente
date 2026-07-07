# FASE 59 - Autenticacao local e perfis

Data: 2026-06-29

## Objetivo

Criar uma camada simples de identificacao local para o painel do Agente 19,
permitindo registrar quem usa o agente e qual perfil operacional foi aplicado.

Esta fase nao cria autenticacao do SEI, nao pede senha do SEI e nao usa cookie,
token ou sessao do navegador.

## Perfis iniciais

| Perfil | Permissoes iniciais |
| --- | --- |
| operador | Importar texto, importar PDF, gerar minuta, triar demanda e criar missao |
| revisor | Gerar minuta, triar demanda e revisar missao |
| gestor | Acessar todos os endpoints locais da fase MVP |

## Mecanismo do MVP

Os endpoints locais protegidos exigem headers:

```text
X-Agente19-User: usuario.local
X-Agente19-Role: operador
```

Perfis validos:

```text
operador
revisor
gestor
```

## Endpoints protegidos

```text
POST /api/import-text
POST /api/import-pdf
POST /api/generate-draft
POST /api/triage-local
POST /api/mission-control
```

## Regras de seguranca

1. Usuario local e obrigatorio.
2. Perfil local e obrigatorio.
3. Perfil invalido e bloqueado.
4. Perfil sem permissao para o endpoint e bloqueado.
5. Headers de senha, cookie, token ou authorization sao bloqueados.
6. Payload com `senha`, `senha_sei`, `password`, `cookie`, `session` ou `token`
   e bloqueado.
7. Nenhuma senha do SEI deve ser enviada ao Agente 19.

## Arquivos implementados

1. `app/core/auth.py`
2. `app/dashboard/local_app.py`
3. `browser_extension/background.js`
4. `browser_extension/content.js`
5. `tests/test_auth.py`

## Criterios de aceite

1. Operador consegue criar missao.
2. Usuario ausente e bloqueado.
3. Perfil invalido e bloqueado.
4. Revisor nao importa texto no MVP.
5. Senha ou token no payload sao bloqueados.
6. `Authorization` e bloqueado no painel local.
7. Usuario local e perfil sao anexados ao payload antes da execucao.

## Evolucao futura

Esta implementacao usa headers por ser MVP local. A evolucao correta e trocar
os headers por login local com sessao propria do painel, mantendo o mesmo modelo
de perfis e permissoes.
