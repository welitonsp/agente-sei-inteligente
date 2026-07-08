# GitHub SEI - catalogo para conhecimento do Agente 19

Data da coleta: 2026-07-08

Este diretorio registra fontes publicas do GitHub sobre SEI/SUPER/SIP,
classificadas para uso na base local do Agente 19.

## Regras

1. Fonte oficial operacional pode alimentar RAG.
2. Fonte tecnica de modulo/API entra como referencia controlada.
3. Automacao, MCP, CLI e extensao entram apenas como alerta de risco.
4. Nenhum conteudo desta pasta autoriza chamada real ao SEI.
5. Nenhum conteudo desta pasta autoriza armazenar usuario, senha, token, cookie,
   certificado ou endpoint institucional.
6. Atos oficiais continuam bloqueados: assinar, tramitar, enviar, concluir, dar
   ciencia, excluir, cancelar, alterar sigilo ou liberar acesso.

## Arquivos

1. `fontes_github_sei.csv`: catalogo de repositorios e prioridade de ingestao.

## Prioridades

```text
P0 = ingerir na RAG como conhecimento oficial de baixo risco
P1 = referencia tecnica controlada, sem execucao
P2 = estudar para UX, riscos e avaliacoes adversariais
HISTORICO = consultar apenas se a fonte atual nao cobrir o tema
```

## Colecoes sugeridas

```text
sei_operacional
sei_admin
sei_api_referencia
sei_modulos_governanca
sei_laboratorio
sei_riscos_automacao
```

## Fontes mais importantes

1. `pengovbr/pen-docs`: manuais atuais do PEN.
2. `pengovbr/wiki-processoeletronico`: wiki institucional.
3. `pengovbr/mod-wssei`: REST/Swagger/API do SEI.
4. `pengovbr/sei-docker`: laboratorio Docker para SEI.
5. `anatelgovbr/mod-sei-ia` e `anatelgovbr/sei-ia`: arquitetura oficial de IA.
6. `SEI-Pro/mcp-seipro`: exemplo de risco por expor muitas ferramentas e
   credenciais.
