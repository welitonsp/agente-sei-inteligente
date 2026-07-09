# Changelog

Todas as entregas relevantes do projeto devem ser registradas aqui.

## [0.5.0-auditoria-nucleo-ia] - 2026-07-08

### Alterado

1. Grafo cognitivo LangGraph (`analyzer_node`, `critic_node`) roteado pela
   camada de provedor (`ai_provider`), respeitando a decisao de Claude como
   provedor padrao e a barreira do `sei_action_guard` antes de toda geracao.
2. Novo modulo `app/intelligence/ai_reasoning.py` (resumo, revisao e analise de
   texto) substituindo `app/intelligence/llm_gemini.py`, que foi removido junto
   do pacote deprecado `google-generativeai` como motor direto.
3. `audit_node` agora persiste auditoria real (`app/core/audit.record`) com
   timestamp UTC, em vez de `print` com timestamp fixo.
4. Shadow Mode: confianca normalizada para a escala 0..1 em `app/agent/agent19.py`.

### Seguranca

1. No critico agora e **fail-closed**: erro/indisponibilidade da auditoria
   automatica nunca marca a minuta como aprovada; exige revisao humana reforcada.
2. Parsing de veredicto por JSON estruturado (fim do `split("\\n")` literal).

### Adicionado

1. System prompts versionados em `knowledge_base/prompts/`
   (`resumidor_administrativo.md`, `guardiao_seguranca.md`).
2. `tests/test_graph_workflow.py`: cobertura do grafo e da camada de raciocinio
   (roteamento sob guarda, fail-closed, loop de auto-correcao, auditoria).

## [0.4.15-knowledge-base-inicial-19crpm] - 2026-06-29

### Adicionado

1. Regras iniciais em `knowledge_base/fluxos_19crpm/` para mencao direta ao
   19 CRPM, apoio operacional e demandas de conhecimento.
2. Evidencias de regra no contrato da triagem local.
3. Resposta do Agente 19 com unidade sugerida, regra aplicada e evidencias.
4. Documento `docs/63-knowledge-base-inicial-19crpm.md`.

### Alterado

1. Normalizacao da triagem para acentos, ordinal `19º` e pontuacao.
2. Testes da knowledge base para validar regra conservadora padrao do 19 CRPM.

### Seguranca

1. Regra sem unidade cadastrada continua sem destino sugerido.
2. Texto sem regra continua exigindo complemento/revisao.
3. Atos oficiais continuam bloqueados e revisao humana permanece obrigatoria.

## [0.4.14-tracing-ferramentas-agente19] - 2026-06-29

### Adicionado

1. `app/agent/tools.py` com registro de ferramentas seguras do agente.
2. `app/agent/tracing.py` com trace operacional sanitizado.
3. `trace.trace_id` no contrato do Agente 19.
4. `mission_trace_id` no contrato do orquestrador de missao.
5. Correlacao entre agente e missao.
6. Documento `docs/62-tracing-ferramentas-agente19.md`.

### Seguranca

1. O trace nao guarda texto integral.
2. Ferramenta `mission_control` e marcada como read-only.
3. Ferramenta desconhecida e negada.
4. Revisao humana obrigatoria permanece no contrato.

## [0.4.13-nucleo-agente-ia-agente19] - 2026-06-29

### Adicionado

1. `app/agent/agent19.py` como nucleo explicito do Agente 19.
2. Endpoint local `POST /api/agent19`.
3. Contrato com identidade do agente, intencao, plano, ferramentas usadas,
   resposta e resultado.
4. Extensao read-only passa a chamar `/api/agent19` para a acao `19 CRPM`.
5. Documento `docs/61-nucleo-agente-ia-agente19.md`.
6. Testes automatizados do nucleo do agente.

### Seguranca

1. O agente usa ferramenta permitida `mission_control`.
2. Revisao humana continua obrigatoria.
3. Atos oficiais continuam bloqueados.
4. O agente nao ganha permissao para abrir links, exportar PDF, clicar no SEI
   ou usar senha/cookie/token/sessao.

## [0.4.12-agente-visual-sei-interesse-19crpm] - 2026-06-29

### Adicionado

1. Botao `19 CRPM` no chat da extensao read-only.
2. Chamada `AGENTE_SEI_MISSION` para o endpoint local `/api/mission-control`.
3. Resposta focada em interesse do 19 CRPM: resumo, prazo, providencia,
   unidade, minuta externa, riscos e pendencias.
4. Preview local com simulacao de missao do 19 CRPM.
5. Documento `docs/60-agente-visual-sei-interesse-19crpm.md`.

### Alterado

1. `browser_extension/manifest.json` atualizado para `0.2.2`.
2. Bloqueio de atos oficiais passa a avaliar o pedido do usuario, evitando falso
   bloqueio quando a propria pagina do SEI contem termos como assinatura.

### Seguranca

1. A extensao continua read-only.
2. Nao abre link do processo automaticamente.
3. Nao exporta PDF automaticamente.
4. Nao usa senha, cookie, token, hash ou sessao do SEI.
5. Nao clica em botoes do SEI.

## [0.4.11-autenticacao-local-perfis] - 2026-06-29

### Adicionado

1. `app/core/auth.py` com autorizacao local por usuario e perfil.
2. Headers locais `X-Agente19-User` e `X-Agente19-Role` nos endpoints do painel.
3. Campo `Perfil local` no painel MVP.
4. Protecao dos endpoints `import-text`, `import-pdf`, `generate-draft`,
   `triage-local` e `mission-control`.
5. Identificacao local da extensao read-only como `extensao.sei`.
6. Documento `docs/59-autenticacao-local-perfis.md`.
7. Testes automatizados de autorizacao local e bloqueio de credenciais.

### Seguranca

1. Usuario local e perfil passam a ser obrigatorios nos endpoints protegidos.
2. Perfil invalido ou sem permissao e bloqueado.
3. Headers/payloads com senha, cookie, token ou authorization sao bloqueados.
4. Senha do SEI continua proibida.

## [0.4.10-pesquisa-github-ecossistema-sei] - 2026-06-29

### Adicionado

1. Pesquisa atualizada de repositorios GitHub do ecossistema SEI/SUPER.
2. Matriz de repositorios em `docs/52-referencias-github-sei.md`.
3. Analise de `mod-wssei`, `sei-docker`, `sei-ia`, `mod-sei-ia`, modulos PEN,
   Protocolo Integrado, Peticionamento, FalaBR e MCP SEI Pro.
4. Decisoes sobre o que pode ser aprendido e o que nao deve ser copiado.

### Seguranca

1. Mantida decisao de nao usar API real sem endpoint autorizado.
2. Mantida proibicao de credenciais SEI em MCP ou ferramenta de LLM.
3. Mantido bloqueio de assinatura, tramitacao, envio, conclusao e ciencia.

## [0.4.9-revisao-mercado-evals-agente] - 2026-06-29

### Adicionado

1. Revisao de mercado do projeto como Agente de IA em `docs/58-revisao-mercado-agente-ia.md`.
2. Suite de avaliacoes de prontidao em `app/evaluation/agent_readiness.py`.
3. Script `scripts/run_agent_evals.py` para executar avaliacoes de comportamento.
4. Testes em `tests/test_agent_readiness_evals.py`.
5. CI passa a executar avaliacoes de agente apos a suite de testes.
6. Plano de testes atualizado com a camada de avaliacao de comportamento.

### Seguranca

1. As avaliacoes validam revisao humana obrigatoria.
2. As avaliacoes validam bloqueio de assinatura, envio, tramitacao, conclusao
   e ciencia automatica.
3. Pedido textual de ato oficial nao libera acao oficial no contrato.

## [0.4.8-orquestrador-missao-agente19] - 2026-06-29

### Adicionado

1. `app/intelligence/mission_control.py` com orquestrador supervisionado do Agente 19.
2. Endpoint local `POST /api/mission-control`.
3. Botao `Missao Agente 19` no painel local.
4. Contrato unico com analise, triagem, minuta, riscos, campos pendentes,
   prontidao operacional e plano de acao humano.
5. Documento `docs/57-orquestrador-missao-agente19.md`.
6. Testes automatizados do orquestrador e do endpoint do painel.

### Seguranca

1. A missao nao acessa o SEI real.
2. A missao nao assina, envia, tramita, conclui, da ciencia ou altera sigilo.
3. Revisao humana permanece obrigatoria mesmo quando a prontidao operacional e alta.
4. Acoes oficiais continuam bloqueadas no contrato.

## [0.4.7-ux-chat-v2-minuta-externa] - 2026-06-23

### Adicionado

1. Barra de status operacional na UI chat: `Somente leitura`, `Backend local`
   e `Revisao humana`.
2. Acao rapida `Minuta`, limitada a rascunho externo para conferencia humana.
3. Fechamento do painel pelo atalho `Esc`.
4. Preview local atualizado com resposta simulada de minuta.
5. Documento `docs/45-ux-chat-v2-minuta-externa.md`.
6. Testes de contrato para a UI chat V2.

### Alterado

1. `browser_extension/manifest.json` atualizado para `0.2.1`.
2. `browser_extension/content.js` passa a formatar minuta como rascunho externo.
3. `browser_extension/content.css` passa a exibir status operacional fixo.

### Seguranca

1. A minuta nao e inserida no SEI pela extensao.
2. A insercao no SEI permanece manual.
3. A extensao continua sem clique automatico, cookie, token, sessao ou ato
   oficial.

## [0.4.6-preview-local-ui-chat] - 2026-06-23

### Adicionado

1. Preview local `browser_extension/preview_chat.html`.
2. Shim local de `chrome.runtime.sendMessage` com resposta simulada.
3. Documento `docs/44-preview-local-ui-chat-agente19.md`.
4. Testes de contrato para preview local.

### Seguranca

1. Preview usa somente dados ficticios.
2. Nao abre SEI real.
3. Nao usa backend real.
4. Nao usa senha, cookie, token ou sessao.
5. Nao executa ato oficial.

## [0.4.5-ui-chat-agente19-sei] - 2026-06-23

### Adicionado

1. UI da extensao reformulada como chat lateral profissional.
2. Botao flutuante compacto `19`.
3. Historico de mensagens do usuario e assistente.
4. Campo de pergunta sobre o processo aberto.
5. Acoes rapidas: capturar tela, resumo, prazos e providencia.
6. Botao de copiar resposta.
7. Documento `docs/43-ui-chat-agente19-sei.md`.

### Alterado

1. `browser_extension/manifest.json` atualizado para `0.2.0`.
2. `browser_extension/content.js` e `content.css` substituem painel simples por chat.
3. Testes da extensao ampliados para validar UI chat e modo read-only.

### Seguranca

1. Chat continua read-only.
2. Sem login, senha, cookie, token ou sessao.
3. Sem clique automatico no SEI.
4. Sem ato oficial.
5. Comunicacao restrita ao backend local `127.0.0.1`.

## [0.4.4-resultado-diagnostico-real-api] - 2026-06-23

### Adicionado

1. Documento `docs/42-resultado-diagnostico-real-api-sei.md`.
2. Tratamento de conexao encerrada pelo host remoto no diagnostico API.
3. Ajuste do script `scripts/sei_api_discovery.py` para rodar diretamente.

### Resultado

1. `mod-wssei-v2`: `404 nao_encontrado`.
2. `mod-wssei-v1`: `404 nao_encontrado`.
3. `sei-soap-wsdl`: indisponivel sem credenciais/sessao; conexao encerrada pelo host remoto.

### Seguranca

1. Diagnostico real executado sem usuario, senha, cookie, token ou sessao.
2. Nenhuma operacao de negocio foi chamada.
3. API real segue nao habilitada.

## [0.4.3-diagnostico-api-sei-wssei] - 2026-06-23

### Adicionado

1. `app/sei/api_discovery.py` para diagnostico seguro de endpoints SEI/WSSEI.
2. `scripts/sei_api_discovery.py` para execucao manual do diagnostico.
3. Testes automatizados em `tests/test_sei_api_discovery.py`.
4. Documento `docs/41-diagnostico-api-sei-wssei.md`.

### Seguranca

1. Diagnostico nao envia usuario, senha, cookie, token ou sessao.
2. Diagnostico nao usa sessao do navegador.
3. Diagnostico nao executa operacao de negocio no SEI.
4. URLs com credenciais sao recusadas.
5. Resultado positivo nao autoriza uso real da API.

## [0.4.2-fase5b-homologacao] - 2026-06-23

### Adicionado

1. `app/sei/minuta_cadastro.py` com contrato de cadastro da minuta.
2. `app/sei/selector_manifest.py` com validacao de manifesto de seletores.
3. `app/sei/fase5b_homologacao.py` com avaliador de prontidao para homologacao.
4. Template `knowledge_base/sei_homologacao/minuta_selectors.template.json`.
5. Testes automatizados em `tests/test_phase5b_homologacao.py`.

### Seguranca

1. `nivel_acesso` passa a ser obrigatorio antes de qualquer minuta real futura.
2. Acesso restrito/sigiloso exige `hipotese_legal`.
3. Campos administrativos podem ser exigidos por tipo documental.
4. Manifesto bloqueia seletores relacionados a atos oficiais.
5. Mesmo pronto para homologacao, `real_write_allowed=false`.
6. Nenhum seletor real foi implementado.
7. Escrita real no SEI continua nao habilitada.

## [0.4.1-patch4-hardening-fase5a] - 2026-06-23

### Adicionado

1. `app/core/safety.py` com `evaluate_safety()` e `assert_safe_environment()`.
2. Flags da FASE 5A em `app/core/config.py`.
3. `app/sei/minuta_token.py` com token HMAC amarrado a processo, tipo e hash.
4. `app/sei/read_only_page.py` para leitura sem expor pagina crua.
5. `app/sei/playwright_session.py` como unico arquivo autorizado a abrir sessao Playwright efemera.
6. `app/sei/minuta_writer.py` como chokepoint de minuta controlada simulada.
7. Testes automatizados em `tests/test_phase5a_minuta_controlada.py`.

### Seguranca

1. `MINUTA_TOKEN_SECRET` padrao e segredo curto bloqueados em `APP_ENV=prod`.
2. `ENABLE_MINUTA_CREATION=true` bloqueado em producao enquanto FASE 5B nao estiver homologada.
3. Startup do painel e desktop chama `assert_safe_environment()`.
4. `MinutaWriter` exige token e valida processo correto.
5. Auditoria da FASE 5A registra `text_hash`, nunca texto integral.
6. Escrita real no SEI permanece como `NotImplementedError`.
7. Teste arquitetural bloqueia uso direto de Playwright fora de `app/sei/playwright_session.py`.

## [0.4.0-enquadramento-arquitetural-sei-particular] - 2026-06-23

### Alterado

1. README reenquadrado como "Agente SEI Inteligente Particular — assistente local supervisionado para analise de processos, geracao de minutas e apoio operacional no SEI."
2. Documentada a premissa de login manual do usuario no SEI Goias.
3. Explicitado que o agente nao guarda senha, cookie, token ou sessao.
4. Explicitado que a sessao Playwright deve ser efemera e que o LLM nao controla o navegador.
5. Roadmap atualizado para FASE 4, FASE 5A, FASE 5B, FASE 6 e FASE 7.
6. Criado documento `docs/fase-5-minuta-controlada.md`.

### Seguranca

1. Registrados allow-list/default-deny, chokepoint, `ReadOnlyPage`, `MinutaWriter`, token de confirmacao, hash de conteudo e feature flags desligadas por padrao.
2. FASE 5A documentada como minuta controlada simulada, sem escrita real no SEI.
3. FASE 5B mantida como futura, condicionada a seletores homologados.
4. Escrita real no SEI continua nao habilitada.
5. PATCH 4 definido como proximo passo de hardening.

## [0.3.7-knowledge-base-local-19crpm] - 2026-06-22

### Adicionado

1. Estrutura `knowledge_base/fluxos_19crpm/` com CSVs locais.
2. Carregador em `app/intelligence/knowledge_base.py`.
3. Triagem e roteamento por regras em `app/intelligence/local_triage.py`.
4. Endpoint local `POST /api/triage-local`.
5. Botao `Triagem local` no painel e no desktop.
6. Documento da Fase 40 em `docs/40-fase-knowledge-base-local-19crpm.md`.
7. Testes automatizados em `tests/test_local_knowledge_base.py`.

### Seguranca

1. Sem regras reais, o sistema retorna `indefinido`.
2. Unidade responsavel nao e inventada.
3. Sugestao exige revisao humana obrigatoria.
4. A triagem nao executa ato oficial no SEI.

## [0.3.6-minutador-local-zero-custo] - 2026-06-22

### Adicionado

1. Minutador local em `app/intelligence/local_minutador.py`.
2. Templates locais em `knowledge_base/templates_minutas/`.
3. Endpoint local `POST /api/generate-draft`.
4. Botao `Gerar minuta local` no painel MVP.
5. Botao `Gerar minuta` no Agente 19 Desktop.
6. Documento da Fase 39 em `docs/39-fase-minutador-local-zero-custo.md`.
7. Testes automatizados em `tests/test_local_minutador.py`.

### Seguranca

1. Minutas sao rascunhos locais e exigem revisao humana.
2. O sistema nao escreve no SEI, nao cria documento oficial e nao assina.
3. Auditoria registra metadados, tipo e confianca, sem persistir texto integral.
4. Acoes oficiais permanecem bloqueadas no contrato.

## [0.3.5-estrategia-zero-custo] - 2026-06-22

### Adicionado

1. Estrategia zero custo em `docs/38-estrategia-zero-custo-sei.md`.
2. Decisao DEC-0012 registrando que o projeto nao deve depender de servico
   pago, API paga, assinatura, RPA pago ou hospedagem paga.

### Alterado

1. Caminho de IA passa a priorizar regras locais, templates, OCR gratuito e
   modelo local opcional, conforme hardware e autorizacao.
2. Minutador por templates locais passa a ser a proxima entrega recomendada
   antes de qualquer IA paga.

### Seguranca

1. Conteudo real do SEI continua proibido em IA externa sem autorizacao formal.
2. Escrita no SEI continua proibida sem homologacao; quando liberada, no maximo
   minuta/rascunho sem assinatura.

## [0.3.4-desktop-navegador-seguro] - 2026-06-22

### Adicionado

1. Aplicacao desktop local em `app/desktop/`, executavel com
   `.venv\Scripts\python.exe -m app.desktop`.
2. Botao para abrir a URL oficial `https://sei.go.gov.br/sei/` em
   navegador/janela separada, sem capturar login ou senha.
3. Painel desktop do Agente 19 para texto colado, PDF manual, resumo, tipo
   provavel, evento/prazo, providencia sugerida e copia do resultado.
4. Comunicacao do desktop restrita ao backend local `http://127.0.0.1:8000`.
5. Documento da Fase 37.2 em `docs/37-fase-desktop-navegador-seguro.md`.
6. Testes de contrato de seguranca do desktop em
   `tests/test_desktop_secure_browser.py`.

### Seguranca

1. O Agente 19 Desktop nao possui campo de senha ou login SEI.
2. Payloads com campos/indicios de credencial sao bloqueados.
3. O desktop nao le cookies, sessao, localStorage/sessionStorage ou headers de
   autenticacao.
4. O desktop nao executa cliques nem atos oficiais no SEI.
5. A extensao Chrome/Edge fica como recurso futuro opcional, dependente de
   autorizacao institucional.

### Riscos conhecidos

1. Uso real com navegador interno ou janela separada depende de homologacao e
   autorizacao institucional.
2. O usuario ainda precisa copiar texto/exportar PDF manualmente do SEI.

## [0.3.3-extensao-sei-readonly] - 2026-06-22

### Adicionado

1. Protótipo de extensão Chrome/Edge em `browser_extension/`, com botão
   flutuante dentro das páginas `https://sei.go.gov.br/sei/*`.
2. Painel lateral in-page para capturar texto visível/selecionado da tela do
   SEI e enviar ao backend local `POST /api/import-text`.
3. Service worker `background.js` chamando apenas `http://127.0.0.1:8000`.
4. Testes de contrato de segurança da extensão
   (`tests/test_browser_extension_contract.py`).
5. Relatorio consolidado de status do projeto em
   `docs/36-relatorio-status-projeto.md`.

### Segurança

1. Extensão não solicita permissão de cookies nem webRequest.
2. Extensão não guarda senha, cookie ou sessão.
3. Extensão não executa clique automático no SEI.
4. Termos de atos oficiais são bloqueados no conteúdo enviado para análise.
5. Modo continua read-only e exige revisão humana.

### Riscos conhecidos

1. Requer instalação manual como extensão sem publicação na loja.
2. Leitura direta da tela do SEI deve ser validada em homologação institucional.
3. Busca/navegação por número de processo e qualquer ato oficial seguem proibidos.

## [0.3.2-pdf-local] - 2026-06-22

### Adicionado

1. Upload/análise local de PDF em `app/intake/pdf_upload.py`, usando `pypdf`
   para extrair texto de PDFs pesquisáveis.
2. Detecção de PDF sem texto extraível, com `status_leitura=ocr_necessario`.
3. Endpoint local `POST /api/import-pdf` e campo de upload no painel MVP.
4. Persistência segura de hash/metadados/resumo estrutural de PDF, sem salvar
   texto integral.
5. Testes automatizados do fluxo PDF (`tests/test_pdf_upload_intake.py`).

### Alterado

1. `requirements.txt`: adiciona `pypdf`.
2. Painel local passa a aceitar texto colado ou PDF.

### Segurança

1. Upload PDF passa pelo guardião antes de leitura/resumo.
2. Auditoria registra hash, quantidade de páginas e contagem de caracteres, sem
   registrar texto integral.
3. Suite local ampliada para 97 testes passando.

### Riscos conhecidos

1. OCR ainda não executa reconhecimento; apenas marca `ocr_necessario`.
2. Autenticação do painel local continua pendente.
3. Triagem real do 19 CRPM segue bloqueada até preencher a knowledge base.

## [0.3.1-painel-local-texto] - 2026-06-22

### Adicionado

1. Painel MVP local em `app/dashboard/local_app.py`, sem dependencias externas,
   executavel com `python -m app.dashboard`.
2. Tela operacional para numero do processo SEI, usuario local, titulo, texto
   copiado, botao de analise e exibicao do resultado estruturado.
3. Endpoint local `POST /api/import-text`, conectado ao backend
   `manual_text.analyze_text`.
4. Testes automatizados do painel local (`tests/test_dashboard_local_app.py`).

### Seguranca

1. Painel nao acessa SEI real, nao pesquisa processo por numero e nao oferece
   botoes de ato oficial.
2. Resultado exibe revisao humana obrigatoria e campos pendentes.
3. Suite local ampliada para 92 testes passando.

### Riscos conhecidos

1. Painel ainda nao tem autenticacao; permitido apenas para MVP local.
2. Upload de PDF/OCR ainda nao implementado.
3. Triagem real do 19 CRPM segue bloqueada ate preencher a knowledge base.

## [0.3-intake-texto-local] - 2026-06-22

### Adicionado

1. Fluxo backend `IMPORT_TEXT` em `app/intake/manual_text.py` para receber texto
   colado no MVP externo/local, sem acessar o SEI real.
2. Persistencia segura de metadados em `Process` e `Document`: hash do texto,
   titulo, origem, classificacao e resumo estrutural; texto integral nao e
   persistido por padrao.
3. Extracao local simples de evento, prazo, data, horario e local para apoiar a
   futura tela de revisao administrativa.
4. Testes automatizados do intake manual (`tests/test_manual_text_intake.py`).

### Seguranca

1. Fluxo passa pelo guardiao (`LER_DOCUMENTO` e `RESUMIR`) antes de registrar a
   analise.
2. Auditoria registra metadados, hash e contagens, sem gravar o texto colado.
3. Toda analise local retorna `revisao_humana_obrigatoria=true`.
4. Suite local ampliada para 89 testes passando.

### Riscos conhecidos

1. Ainda nao ha tela web consumindo o backend de texto colado.
2. Extracao e heuristica; baixa confianca permanece em revisao humana.
3. PDF, OCR, IA/RAG e triagem 19 CRPM real continuam pendentes.

## [0.2.1-ci-gate] - 2026-06-22

### Adicionado

1. Workflow GitHub Actions em `.github/workflows/ci.yml` para rodar testes em
   Python 3.11 e 3.13.
2. Gate simples de segredos em `scripts/check_no_secrets.py`, varrendo arquivos
   conhecidos pelo Git e novos nao ignorados, bloqueando `.env`, refresh token,
   client secret, URL ICS, chaves de API e private keys concretas.
3. Testes automatizados do scanner de segredos (`tests/test_secret_scanner.py`).

### Seguranca

1. CI passa a executar `scripts/check_no_secrets.py` antes do `pytest`.
2. Varredura local confirmou ausencia de segredos concretos nos arquivos
   conhecidos pelo Git e novos nao ignorados.
3. Suite local ampliada para 84 testes passando.

### Riscos conhecidos

1. PR #1 aberto em modo draft e GitHub Actions aprovado em Python 3.11/3.13.
2. Protecao de branch ainda precisa ser configurada no GitHub.
3. OAuth do Google continua pendente de conclusao (client secret + refresh token).

## [0.2-fundacao-tecnica] - 2026-06-21

### Adicionado

1. Estrutura `app/` e fundacao tecnica de seguranca:
   `permissions.py` (lista positiva/proibida/sensivel), `sei_action_guard.py`
   (guardiao com negacao por padrao), `security_filter.py` (sanitiza segredos),
   `config.py`, `logging.py` e `audit.py`.
2. Banco SQLite com as 8 entidades de `docs/11` (`storage/db.py`, `models.py`).
3. Skill `agenda-oficiais` (`integrations/agenda_service.py`): titulo padrao,
   observacao, lembretes por tipo, dedup local e guard com aprovacao humana.
4. Backends de calendario: `InMemory` (dry-run) e `Google` (OAuth, import tardio).
5. Resolucao de convidados pelo marcador "OFICIAIS" via People API
   (`integrations/contacts_resolver.py`).
6. Leitor iCal read-only e dedup contra o calendario real
   (`integrations/ics_reader.py`, `find_equivalent`).
7. Cliente OAuth real Calendar+People (`integrations/google_auth.py`,
   `integrations/runtime.py`) e scripts `google_oauth_setup.py`,
   `google_validate.py`, `init_db.py`.
8. Suite de testes (81 casos) e documento de handoff `docs/35`.

### Alterado

1. `.env.example`: variaveis de OAuth, `CALENDAR_BACKEND`, `OFFICERS_SOURCE`,
   `OFFICERS_CONTACT_LABEL`, `GOOGLE_CALENDAR_ICS_URL`.
2. `.gitignore`: ignora arquivos de credencial/token Google.

### Segurança

1. Atos oficiais do SEI bloqueados no `sei_action_guard.py` (gate testado).
2. Senha/cookie/token/URL ICS sanitizados antes de log e auditoria.
3. Refresh token e client secret tratados como segredos (somente `.env`).
4. Convites e e-mails dos Oficiais: auditoria registra so a contagem.
5. Modo dry-run permanece como padrao ate o OAuth completo.

### Riscos conhecidos

1. CI no GitHub Actions configurado em 2026-06-22 e aprovado no PR #1.
2. Knowledge base do 19 CRPM ainda usa templates.
3. OAuth do Google pendente de conclusao (client secret + refresh token).
4. PR #1 aberto em modo draft; merge para `main` pendente de revisao humana.

## [0.1-docs] - 2026-06-21

### Adicionado

1. Documentacao base do Agente SEI Inteligente.
2. Politicas de seguranca, identidade, dados e SEI.
3. Estrategia sem modulo oficial SEI IA.
4. Requisito do robozinho SEI.
5. Skills especialistas e contratos.
6. Matriz de conformidade.
7. Checklist de processos de desenvolvimento.
8. Regras de Git, IA, Commit, Push, PR e Merge.
9. Regra de documentacao continua.
10. Prompt mestre para Claude Code.

### Alterado

1. README atualizado com indice documental.

### Segurança

1. Atos oficiais no SEI bloqueados por politica.
2. Conteudo real do SEI proibido em IA externa sem autorizacao formal.
3. Usuario/senha individuais preservados.

### Riscos conhecidos

1. Nao ha codigo de aplicacao.
2. Knowledge base do 19 CRPM ainda usa templates.
3. Robozinho real/extensao esta fora do MVP.
