# Status Atual do Projeto - Agente 19 (19º CRPM)

## Últimas Atualizações (Julho 2026)
O projeto deixou de ser um MVP de "leitura heurística engessada" e foi oficialmente elevado ao patamar **Autônomo com Inteligência Artificial de Nível Big Tech**.

### 1. Novo Motor de IA
* **Remoção de Heurísticas:** Desligamos o analisador local de expressões regulares (`manual_text.py` legado).
* **Integração LLM Oficial:** Implementamos a conexão direta com o motor do Google (`google-generativeai`).
* **Modelo Utilizado:** **Gemini 2.5 Flash**. Optou-se pela versão Flash porque ela tem a cota gratuita dimensionada para suportar a quantidade massiva de leitura de processos, além de ser excepcionalmente veloz. (O Gemini 2.5 Pro bloqueou o acesso por esgotamento de cota do Free Tier).
* **Autenticação:** O sistema agora exige uma `GEMINI_API_KEY` válida configurada no arquivo `.env`.

### 2. Leitura Autônoma de Processo (RPA + Scraping)
* **Funcionalidade:** Quando o usuário joga um Número Único de Processo (NUP) no chat minimalista da extensão, o bot (Javascript - `content.js`) identifica o NUP e automaticamente:
  1. Força uma pesquisa no SEI.
  2. Varre toda a árvore de documentos (`ifrArvore`) de forma invisível via `fetch` AJAX.
  3. Extrai o texto limpo de TODOS os documentos do processo.
  4. Junta tudo (até o limite de 60.000 caracteres) e envia para o backend local.
* **Interface:** A interface minimalista "Modo ZEN" está perfeita, sem botões de "Assunto" ou "Prazo", operando 100% como chat conversacional.

### 3. Próximos Passos (Amanhã)
1. **Validar Resposta do Gemini:** Com o servidor reiniciado utilizando o `Gemini 2.5 Flash`, avaliar a qualidade do "resumo executivo" gerado e se ele atende à precisão militar exigida.
2. **Engenharia de Prompt Avançada:** Refinar as instruções (system prompt) dentro de `app/intelligence/llm_gemini.py` para que o Gemini responda exatamente como um Oficial do Estado-Maior, com tópicos diretos: Fato, Prazo e Providências Sugeridas (minutas).
3. **Persistência de Memória de Chat (Opcional):** Hoje a cada reload de tela o chat fica limpo. Se necessário, armazenar o contexto da conversa.

## Como retomar os trabalhos amanhã
O usuário deve:
1. Garantir que a tela do servidor CMD está fechada.
2. Executar `Iniciar_Agente_19.bat`.
3. Abrir o Chrome (aba do SEI) e pressionar F5.
4. Digitar o número de um processo no Chat e verificar a resposta completa!
