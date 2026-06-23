# Fase 44 - Preview local da UI Chat do Agente 19

## Objetivo

Permitir homologacao visual da interface do Agente 19 em formato de chat sem
abrir o SEI real, sem instalar extensao institucional e sem usar dados
sensiveis.

## Arquivo criado

```text
browser_extension/preview_chat.html
```

## Como abrir

Abra no navegador:

```text
C:\ADM PMGO\browser_extension\preview_chat.html
```

Ou, pelo explorador de arquivos, de duplo clique em:

```text
browser_extension/preview_chat.html
```

## O que a previa simula

1. Tela visual semelhante ao ambiente SEI.
2. Processo ficticio `202600000123456`.
3. Documento ficticio com prazo simulado.
4. Botao flutuante `19`.
5. Chat lateral do Agente 19.
6. Captura de texto visivel.
7. Resposta simulada do backend.

## O que a previa nao faz

1. Nao abre o SEI real.
2. Nao usa login.
3. Nao usa senha.
4. Nao usa cookie.
5. Nao usa token.
6. Nao usa sessao.
7. Nao chama backend real.
8. Nao executa ato oficial.

## Criterios de avaliacao visual

1. O botao `19` deve aparecer sem atrapalhar a tela.
2. O chat deve abrir e fechar facilmente.
3. As mensagens devem ser legiveis.
4. O campo de pergunta deve funcionar em layout desktop e mobile.
5. As acoes rapidas devem ser claras.
6. O aviso de seguranca deve estar sempre visivel.
7. A resposta deve ser facil de copiar.

## Status

```text
PREVIEW_LOCAL_IMPLEMENTADO
```

## Proximo passo

Homologar visualmente com o usuario e ajustar dimensoes, cores, textos e
posicionamento antes de testar a extensao no SEI real.
