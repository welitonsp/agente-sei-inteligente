# Fase 43 - UI Chat do Agente 19 na tela do SEI

## Objetivo

Definir e prototipar o formato visual do Agente 19 dentro da tela do SEI como
um chat lateral profissional, moderno e supervisionado.

## Decisao de produto

O formato principal do Agente 19 na tela do SEI sera:

```text
Botao flutuante -> Chat lateral -> Perguntas e acoes rapidas -> Resposta do agente
```

O usuario, ja logado manualmente no SEI, abre o Agente 19 e conversa com ele
sobre o processo/documento visivel.

## O que foi implementado no prototipo

1. Botao flutuante compacto com identidade `19`.
2. Painel lateral em formato de chat.
3. Cabecalho profissional com nome e subtitulo.
4. Campo de processo e titulo.
5. Aviso fixo de seguranca.
6. Historico de mensagens.
7. Campo de pergunta.
8. Acoes rapidas:
   - Capturar tela;
   - Resumo;
   - Prazos;
   - Providencia.
9. Botao de copiar resposta.
10. Respostas formatadas como mensagens do assistente.

## Limites mantidos

1. Nao pede login.
2. Nao pede senha.
3. Nao captura cookie.
4. Nao captura token.
5. Nao captura sessao.
6. Nao usa `localStorage` ou `sessionStorage`.
7. Nao clica no SEI.
8. Nao assina.
9. Nao tramita.
10. Nao envia processo.
11. Nao conclui.
12. Nao altera documento ou processo.

## Comunicacao

O chat continua enviando texto apenas ao backend local:

```text
http://127.0.0.1:8000/api/import-text
```

## Status

```text
PROTOTIPO_CHAT_READONLY_IMPLEMENTADO
```

Uso real dentro do ambiente institucional ainda depende de autorizacao e
homologacao da extensao.

## Proximo passo

1. Rodar backend local.
2. Carregar a extensao em modo desenvolvedor.
3. Abrir SEI manualmente com usuario real.
4. Testar com processo/conteudo anonimizado ou nao sensivel.
5. Registrar evidencias visuais e feedback de usabilidade.
