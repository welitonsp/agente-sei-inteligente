# Status Atual do Projeto - Agente 19 (19º CRPM)

## Últimas Atualizações (Julho 2026)
O projeto deixou de ser um MVP de "leitura heurística engessada" e foi oficialmente elevado ao patamar **Autônomo com Inteligência Artificial de Nível Big Tech**.

### 1. Motor de IA (auditoria de julho/2026: camada de provedor sob guarda)
* **Camada de provedor com papéis lógicos:** toda geração passa por
  `app/intelligence/ai_provider.py` (`get_ai_provider`), que consulta o
  `sei_action_guard` ANTES de qualquer chamada de rede. O prompt nunca é a barreira.
* **Claude é o provedor padrão** (`claude-opus-4-8`); Gemini e `EchoProvider`
  (offline/custo zero) continuam disponíveis por configuração.
* **Grafo LangGraph roteado pelo provedor:** `analyzer_node` e `critic_node`
  usam `app/intelligence/ai_reasoning.py` (substituiu o antigo `llm_gemini.py`,
  removido). O nó crítico é **fail-closed** e o `audit_node` persiste auditoria real.
* **Prompts versionados:** system prompts em `knowledge_base/prompts/`.
* **Offline por padrão nos testes:** `AI_PROVIDER=echo`; credencial só é exigida
  quando o provedor real é selecionado.

### 2. Leitura Autônoma de Processo (RPA + Scraping)
* **Funcionalidade:** Quando o usuário joga um Número Único de Processo (NUP) no chat minimalista da extensão, o bot (Javascript - `content.js`) identifica o NUP e automaticamente:
  1. Força uma pesquisa no SEI.
  2. Varre toda a árvore de documentos (`ifrArvore`) de forma invisível via `fetch` AJAX.
  3. Extrai o texto limpo de TODOS os documentos do processo.
  4. Junta tudo (até o limite de 60.000 caracteres) e envia para o backend local.
* **Interface:** A interface minimalista "Modo ZEN" está perfeita, sem botões de "Assunto" ou "Prazo", operando 100% como chat conversacional.

### 3. Próximos Passos (Amanhã)
1. **Validar Resposta do Gemini:** Com o servidor reiniciado utilizando o `Gemini 2.5 Flash`, avaliar a qualidade do "resumo executivo" gerado e se ele atende à precisão militar exigida.
2. **Engenharia de Prompt Avançada:** Refinar os system prompts versionados em `knowledge_base/prompts/` (`resumidor_administrativo.md`, `guardiao_seguranca.md`) para que a IA responda como um Oficial do Estado-Maior, com tópicos diretos: Fato, Prazo e Providências Sugeridas (minutas).
3. **Persistência de Memória de Chat (Opcional):** Hoje a cada reload de tela o chat fica limpo. Se necessário, armazenar o contexto da conversa.

## Como retomar os trabalhos amanhã
O usuário deve:
1. Garantir que a tela do servidor CMD está fechada.
2. Executar `Iniciar_Agente_19.bat`.
3. Abrir o Chrome (aba do SEI) e pressionar F5.
4. Digitar o número de um processo no Chat e verificar a resposta completa!
