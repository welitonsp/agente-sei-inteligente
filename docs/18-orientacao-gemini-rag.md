# Orientacao para usar Gemini como auxiliar do Agente SEI

## Resposta curta

Sim, podemos usar Gemini como auxiliar inteligente do agente. O uso correto e criar uma base de conhecimento com os documentos do SEI e fazer o agente consultar essa base antes de responder, classificar, resumir ou gerar minuta.

Esse padrao se chama RAG: Retrieval Augmented Generation. Em portugues simples: o agente pesquisa nos documentos oficiais primeiro e so depois usa a IA para montar a resposta.

## O que nao devemos fazer

Nao devemos entregar ao Gemini o poder de executar atos no SEI.

Gemini pode:

1. Ler contexto.
2. Resumir.
3. Classificar.
4. Explicar procedimento.
5. Identificar prazo ou evento.
6. Sugerir providencia.
7. Gerar minuta.

Gemini nao pode:

1. Assinar.
2. Enviar processo.
3. Tramitar.
4. Excluir.
5. Cancelar.
6. Dar ciencia.
7. Liberar acesso externo.
8. Alterar sigilo.

## Tres formas de usar Gemini

### Opcao 1 - Files API para perguntas pontuais

Usa os PDFs diretamente em uma chamada. Serve para analise rapida ou teste.

Uso recomendado:

1. Prototipo.
2. Leitura de um PDF especifico.
3. Validar se Gemini entende o documento.

Limite:

1. Nao e a melhor opcao para uma biblioteca permanente.
2. Pode ficar caro ou lento se reenviar os mesmos PDFs sempre.

### Opcao 2 - File Search do Gemini

Cria uma biblioteca pesquisavel no proprio Gemini. O Gemini importa, divide em partes, indexa e usa busca semantica para responder com base nos documentos.

Uso recomendado para este projeto:

1. Criar uma store `sei-19crpm-manual`.
2. Enviar o Manual do Usuario SEI.
3. Enviar o manual de WebServices com metadado de risco.
4. Consultar essa store no agente classificador, resumidor e minutador.

Vantagem:

1. Mais rapido de construir.
2. Menos codigo proprio.
3. Bom para prototipo e MVP.

Atencao:

1. Os documentos vao para infraestrutura Google.
2. Precisa de chave de API.
3. Deve haver autorizacao para enviar documentos institucionais ou sensiveis.
4. O manual de WebServices nao deve virar permissao de execucao.
5. Conteudo vivo extraido de processos SEI nao deve ser enviado para Gemini sem autorizacao formal.

### Opcao 3 - RAG local

O projeto extrai texto dos PDFs, divide em blocos, cria embeddings e salva localmente em banco vetorial.

Uso recomendado quando:

1. Houver restricao para enviar documentos para API externa.
2. A unidade quiser controle total dos dados.
3. O sistema precisar funcionar em ambiente mais fechado.

Stack possivel:

```text
pypdf ou PyMuPDF -> chunking -> embeddings -> FAISS/Chroma/SQLite-vec -> Gemini ou modelo local
```

## Recomendacao para o projeto

Minha recomendacao tecnica:

1. Fazer MVP com Gemini File Search se houver autorizacao para usar API externa.
2. Manter desenho preparado para trocar por RAG local depois.
3. Separar base de conhecimento em colecoes:
   - `manual-sei-operacional`
   - `sei-webservices-tecnico`
   - `modelos-pmgo`
   - `fluxos-19crpm`
4. Marcar documentos de WebServices como `tecnico_restrito`.
5. Restringir ferramentas de execucao no backend, nao no prompt.

## Fluxo recomendado do agente com biblioteca

```text
Usuario faz pergunta ou envia documento
        |
        v
Agente identifica intencao
        |
        v
Busca trechos relevantes na biblioteca SEI
        |
        v
Gemini recebe pergunta + trechos encontrados + regras de seguranca
        |
        v
Resposta estruturada: resumo, classificacao, prazo, evento ou minuta
        |
        v
Backend valida permissoes
        |
        v
Pagina web mostra resultado para revisao humana
```

## Prompt base do auxiliar SEI

```text
Voce e um auxiliar administrativo especializado no SEI e na rotina do 19 CRPM.
Use somente o contexto recuperado da base de conhecimento e os dados fornecidos pelo usuario.
Quando nao houver informacao suficiente, diga que precisa de revisao humana.
Nunca recomende assinatura, envio, tramitacao, exclusao, cancelamento, ciencia automatica,
liberacao de acesso externo ou alteracao de sigilo como acao automatica.
Classifique a resposta com nivel de confianca e informe quais campos precisam de validacao.
```

## Exemplo de saida estruturada

```json
{
  "tipo": "EVENTO",
  "assunto": "Reuniao operacional",
  "resumo": "Convocacao para reuniao com data, horario e local informados.",
  "evento": {
    "titulo": "Reuniao operacional",
    "data": "2026-07-01",
    "horario": "09:00",
    "local": "19 CRPM"
  },
  "providencia_sugerida": "Criar evento no Google Agenda e alertar oficiais.",
  "acoes_permitidas": ["CRIAR_EVENTO_AGENDA", "ENVIAR_ALERTA"],
  "acoes_bloqueadas": [],
  "confianca": 0.92,
  "revisao_humana": false
}
```

## Onde Gemini entra na arquitetura

Gemini entra em `app/intelligence/`, nao em `app/sei/`.

Arquivos futuros sugeridos:

```text
app/intelligence/gemini_client.py
app/intelligence/knowledge_retriever.py
app/intelligence/sei_rag_assistant.py
app/intelligence/structured_outputs.py
```

O modulo `app/sei/` continua protegido por:

```text
app/sei/sei_action_guard.py
app/core/permissions.py
```

## Passo a passo recomendado

### Passo 1 - Confirmar politica de dados

Decidir se os PDFs podem ser enviados para o Gemini.

Se forem manuais, modelos ou documentos autorizados, usar File Search.

Se forem processos/documentos reais do SEI sem autorizacao, usar RAG local ou analise local temporaria.

### Passo 2 - Preparar base

Organizar documentos em:

```text
knowledge_base/manual_sei/
knowledge_base/sei_webservices/
knowledge_base/modelos_pmgo/
knowledge_base/fluxos_19crpm/
```

### Passo 3 - Criar ingestao

Criar script para:

1. Ler PDF.
2. Extrair texto.
3. Dividir em blocos.
4. Gerar metadados.
5. Enviar para File Search ou salvar em banco local.

### Passo 4 - Criar perguntas de teste

Exemplos:

1. O que e retorno programado no SEI?
2. Qual a diferenca entre minuta e documento assinado?
3. O agente pode dar ciencia automaticamente?
4. Quais dados preciso para criar evento na agenda?
5. Quais operacoes de WebServices sao apenas consulta?

### Passo 5 - Integrar ao painel web

Na pagina web, criar uma area:

```text
Auxiliar SEI
```

Funcoes:

1. Perguntar ao manual.
2. Explicar procedimento.
3. Gerar resumo com fonte.
4. Identificar prazo.
5. Gerar minuta para revisao.

### Passo 6 - Travar execucao

Antes de qualquer acao externa:

1. Checar permissao.
2. Checar confianca.
3. Checar revisao humana.
4. Registrar log.

## Dependencias iniciais

Se usarmos Gemini:

```text
google-genai
pypdf
python-dotenv
```

Comando futuro:

```text
python -m pip install google-genai pypdf python-dotenv
```

## Referencias oficiais consultadas

1. Gemini File Search: https://ai.google.dev/gemini-api/docs/file-search
2. Gemini Document Processing: https://ai.google.dev/gemini-api/docs/document-processing
3. Google GenAI SDK: https://ai.google.dev/gemini-api/docs/migrate
4. Gemini Embeddings: https://ai.google.dev/gemini-api/docs/embeddings
