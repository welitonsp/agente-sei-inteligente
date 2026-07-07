# FASE 60 - Agente visual no SEI com interesse do 19 CRPM

Data: 2026-06-29

## Objetivo

Evoluir a extensao read-only para que o Agente 19 apareca como assistente visual
na tela do SEI e tenha uma acao direta para analisar o processo aberto,
filtrando o que interessa ao 19 CRPM.

## Escopo implementado

1. Botao rapido `19 CRPM` no chat lateral.
2. Chamada ao endpoint local `POST /api/mission-control`.
3. Captura apenas de texto visivel ou selecionado.
4. Processo detectado automaticamente quando o numero aparece na pagina.
5. Resposta estruturada com:
   - interesse do 19 CRPM;
   - assunto/tipo;
   - resumo;
   - prazo;
   - providencia sugerida;
   - unidade sugerida;
   - minuta externa;
   - prontidao, riscos e pendencias.

## Limites mantidos

O Agente 19 nao:

1. abre link do processo sozinho;
2. pesquisa processo por numero;
3. exporta PDF automaticamente;
4. usa senha, cookie, token, hash ou sessao do SEI;
5. clica em botoes do SEI;
6. assina, tramita, envia, conclui ou da ciencia.

## Fluxo operacional seguro

1. O usuario entra no SEI com sua propria conta.
2. O usuario abre o processo manualmente.
3. O usuario abre o Agente 19.
4. O usuario clica em `19 CRPM`.
5. O agente le o texto visivel ou selecionado.
6. O backend local roda a missao supervisionada.
7. O usuario revisa o resultado antes de qualquer providencia.

## Observacao sobre PDF completo

Para ler o processo inteiro, o caminho seguro no MVP continua sendo:

1. usuario exporta/baixa o PDF manualmente no SEI;
2. usuario envia o PDF ao painel local;
3. Agente 19 analisa o PDF fora do SEI.

Automatizar exportacao do PDF fica fora desta fase e depende de homologacao
read-only especifica.

## Arquivos alterados

1. `browser_extension/content.js`
2. `browser_extension/content.css`
3. `browser_extension/background.js`
4. `browser_extension/preview_chat.html`
5. `browser_extension/manifest.json`
6. `tests/test_browser_extension_contract.py`

## Criterios de aceite

1. Extensao mostra botao `19 CRPM`.
2. Botao `19 CRPM` chama `AGENTE_SEI_MISSION`.
3. Background usa `/api/mission-control`.
4. Extensao continua sem `cookies`, `webRequest`, `document.cookie`,
   `localStorage`, `sessionStorage`, `.click()` ou `dispatchEvent()`.
5. Preview local simula resposta de interesse do 19 CRPM.
