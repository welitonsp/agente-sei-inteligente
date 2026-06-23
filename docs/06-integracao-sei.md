# Integracao com SEI

## URL oficial

```text
https://sei.go.gov.br/sei/
```

## Enquadramento atual

O projeto nao possui autorizacao de API oficial, WSSEI, modulo oficial SEI IA ou acesso da TI. A integracao deve ser tratada como particular/local e supervisionada.

Modo permitido:

```text
assistido_particular_local
```

Isso significa que o usuario humano abre o SEI, faz login manualmente com sua propria conta e mantem controle da sessao. O agente pode apoiar leitura, resumo, classificacao, deteccao de prazo, sugestao de providencia e geracao de minuta fora do SEI.

O agente nao deve:

1. Guardar usuario ou senha.
2. Capturar cookie, token ou sessao.
3. Persistir perfil do navegador.
4. Reutilizar sessao de outro usuario.
5. Executar em segundo plano no SEI.
6. Praticar atos oficiais.

## Separacao entre LLM e navegador

O LLM nao controla o navegador. Ele nao escolhe seletor, nao clica, nao navega e nao decide acao oficial.

Permitido ao LLM:

1. Analisar texto.
2. Classificar assunto.
3. Detectar prazo/evento.
4. Sugerir providencia.
5. Gerar conteudo de minuta.

Qualquer interacao com a tela do SEI deve ser codigo deterministico, auditado e protegido por allow-list/default-deny.

## O que o agente pode fazer

1. Abrir sessao com login manual do usuario.
2. Ler processo aberto.
3. Confirmar numero do processo.
4. Ler arvore de documentos.
5. Ler conteudo visivel.
6. Resumir o processo.
7. Classificar o assunto.
8. Detectar prazos.
9. Sugerir providencia.
10. Gerar minuta fora do SEI.
11. Preparar criacao controlada de minuta no SEI, ainda simulada na FASE 5A.

## O que o agente nunca deve fazer

1. Guardar senha.
2. Capturar cookie, token ou sessao.
3. Persistir perfil do navegador.
4. Assinar documento.
5. Tramitar processo.
6. Enviar processo.
7. Concluir processo.
8. Dar ciencia.
9. Cancelar documento.
10. Excluir documento.
11. Liberar acesso externo.
12. Enviar e-mail pelo SEI.
13. Criar tipo de documento no cadastro administrativo do SEI.

## Camadas de protecao

1. Allow-list/default-deny.
2. Chokepoint de leitura.
3. `ReadOnlyPage`.
4. `MinutaWriter`.
5. Token de confirmacao.
6. Verificacao do processo certo antes de escrever.
7. Hash de conteudo.
8. Feature flags desligadas por padrao.
9. Auditoria sem texto integral.
10. Sessao efemera.

## Fases SEI

### FASE 4 - leitura/análise supervisionada

O agente le somente o processo aberto pelo usuario, por sessao manual e efemera, sem capturar credenciais.

### FASE 5A - minuta controlada simulada

Arquitetura segura para minuta, sem escrita real no SEI.

Regras:

1. Token de confirmacao amarrado a processo + tipo de documento + hash do texto.
2. Verificacao do processo correto.
3. Allow-list separada para escrita controlada.
4. `ENABLE_MINUTA_CREATION=false` por padrao.
5. Stubs `NotImplementedError` para UI real.

### FASE 5B - futura

Somente apos homologacao, o agente podera criar uma minuta usando um tipo de documento ja existente no SEI, preencher cadastro, inserir texto no editor, salvar a minuta e parar.

Nao podera assinar, tramitar, enviar, concluir, dar ciencia, cancelar, excluir ou liberar acesso externo.

### FASE 5B-homologacao

Preparacao implementada sem escrita real:

1. Cadastro da minuta exige tipo de documento, nivel de acesso e `text_hash`.
2. Acesso restrito/sigiloso exige hipotese legal.
3. Campos como descricao, interessado e destinatario podem ser obrigatorios por tipo documental.
4. Manifesto de seletores exige status `homologado` para todos os seletores minimos.
5. Seletores de atos oficiais sao bloqueados.
6. `real_write_allowed=false` mesmo quando a prontidao de homologacao estiver positiva.

### FASE 6 - agenda/notificacoes

Integracao com agenda e notificacoes deve continuar fora do SEI, com revisao humana e custo zero por padrao.

### FASE 7 - hardening/auditoria final

Revisao de seguranca, testes arquiteturais e bloqueios de producao antes de qualquer uso real sensivel.

## Variaveis relevantes

```env
ENABLE_SEI_BROWSER_AUTOMATION=false
ENABLE_MINUTA_CREATION=false
MINUTA_TOKEN_SECRET=dev-insecure-trocar-em-producao
LOG_FULL_TEXT=false
ALLOW_OFFICIAL_SEI_ACTIONS=false
```

## Criterios antes de ativar qualquer escrita real

1. Seletores homologados em ambiente seguro.
2. Teste arquitetural impedindo uso direto de Playwright fora dos arquivos permitidos.
3. `MINUTA_TOKEN_SECRET` forte e nao padrao.
4. `ENABLE_MINUTA_CREATION=true` proibido em producao enquanto FASE 5B nao estiver homologada.
5. Auditoria apenas por hash/metadados.
6. Revisao humana antes de salvar minuta.
7. Escrita real mantida como `NotImplementedError` ate aceite formal da FASE 5B.

## Diagnostico seguro de API/WSSEI

O projeto possui diagnostico local para verificar se existem endpoints provaveis
de `mod-wssei` ou WSDL nativo:

```bat
.venv\Scripts\python.exe scripts\sei_api_discovery.py
```

Esse diagnostico nao envia usuario, senha, cookie, token ou sessao. Ele nao
chama operacoes de negocio e nao autoriza uso real. Se algum endpoint responder,
o resultado deve ser tratado apenas como evidencia para decisao humana.

Resultado real registrado em `docs/42-resultado-diagnostico-real-api-sei.md`:
os caminhos publicos padrao de `mod-wssei` retornaram 404 e o WSDL nativo ficou
indisponivel sem credenciais/sessao. Portanto, API real continua fora do caminho
imediato do projeto.
