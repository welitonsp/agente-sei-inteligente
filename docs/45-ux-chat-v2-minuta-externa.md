# Fase 45 - UX Chat V2 e minuta externa supervisionada

## Objetivo

Evoluir a interface do Agente 19 na tela do SEI para um fluxo mais profissional,
com indicadores claros de seguranca e uma acao de minuta que gera apenas
rascunho externo para revisao humana.

## Implementado

1. Barra de status operacional no chat:
   - `Somente leitura`;
   - `Backend local`;
   - `Revisao humana`.
2. Acao rapida `Minuta`.
3. Formatacao especifica para rascunho externo de minuta.
4. Fechamento do painel pelo atalho `Esc`.
5. Preview local atualizado com resposta simulada de minuta.
6. Testes de contrato da extensao atualizados.

## Contrato de seguranca

1. A minuta gerada e apenas texto externo.
2. A insercao no SEI permanece manual.
3. O Agente 19 nao clica no SEI.
4. O Agente 19 nao cria documento oficial.
5. O Agente 19 nao assina, tramita, envia, conclui, da ciencia, cancela ou
   exclui documento/processo.
6. O Agente 19 nao acessa senha, cookie, token ou sessao.

## Como avaliar

Abra:

```text
C:\ADM PMGO\browser_extension\preview_chat.html
```

Depois:

1. Clique no botao `19`.
2. Confira se a barra de status aparece no topo do chat.
3. Clique em `Capturar`.
4. Clique em `Minuta`.
5. Verifique se a resposta aparece como rascunho externo e exige conferencia
   humana.
6. Pressione `Esc` para fechar o painel.

## Status

```text
UX_CHAT_V2_IMPLEMENTADA
```

## Proximo passo

Homologar visualmente com o usuario e ajustar posicionamento, largura, textos e
contraste antes de qualquer teste em SEI real autorizado.
