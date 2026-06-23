# Registro de decisoes

Este documento registra decisoes oficiais do projeto.

## Formato

```text
ID:
Data:
Responsavel:
Status:
Contexto:
Decisao:
Motivo:
Impacto:
Risco:
Arquivos afetados:
Proximo passo:
```

## DEC-0001

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O modulo oficial SEI IA nao pode ser instalado no ambiente institucional.  
Decisao: Adotar arquitetura externa/local assistida, sem modulo interno no SEI.  
Motivo: Reduzir risco tecnico, institucional e de rastreabilidade.  
Impacto: Robozinho sera painel/extensao local read-only em fase futura; MVP usa texto colado e PDF.  
Risco: Menor integracao inicial com SEI.  
Arquivos afetados: `docs/21`, `docs/22`, `docs/25`, `docs/26`.  
Proximo passo: Implementar fundacao tecnica e painel MVP externo/local.

## DEC-0002

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O SEI registra a autoria das acoes por usuario.  
Decisao: Cada servidor deve usar seu proprio usuario e senha; o agente nao pode usar conta unica nem guardar senha.  
Motivo: Preservar rastreabilidade, responsabilidade e seguranca institucional.  
Impacto: O agente so atua apos autenticacao manual do servidor.  
Risco: Menos automacao, mais seguranca.  
Arquivos afetados: `docs/20`, `docs/21`, `docs/22`.  
Proximo passo: Manter bloqueio de login automatico em testes.

## DEC-0003

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: Conteudo real do SEI pode conter dados sensiveis.  
Decisao: Conteudo vivo do SEI nao deve ser enviado para IA externa sem autorizacao formal.  
Motivo: Protecao de dados e reducao de risco institucional.  
Impacto: MVP usa modo local/efemero; Gemini pode ser usado para manuais e materiais autorizados.  
Risco: Algumas analises podem exigir modelo local ou processamento limitado.  
Arquivos afetados: `docs/18`, `docs/25`, `.env.example`.  
Proximo passo: Implementar politica `SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT=false`.

## DEC-0004

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: Desenvolvimento com IA precisa de rastreabilidade.  
Decisao: Codigo de aplicacao deve entrar por branch e PR; commits diretos na main ficam restritos a documentacao enquanto nao houver codigo.  
Motivo: Controlar qualidade, seguranca e revisao humana.  
Impacto: Mudancas de codigo exigem PR, testes e revisao.  
Risco: Mais processo, menos improviso.  
Arquivos afetados: `docs/28`.  
Proximo passo: Configurar protecao da branch main quando o codigo iniciar.

## DEC-0005

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O projeto passara a usar Claude Code como agente de desenvolvimento assistido.  
Decisao: Criar e usar prompt mestre operacional para Claude Code, obrigando leitura da documentacao, respeito a matriz de conformidade, politica de dados, regras Git/IA e documentacao continua.  
Motivo: Evitar que o agente de codigo execute fora do escopo, pule seguranca ou perca rastreabilidade.  
Impacto: Claude Code deve iniciar pela fundacao tecnica e manter SEI real, robozinho real e IA externa com conteudo vivo fora do MVP.  
Risco: Prompt nao substitui revisao humana nem testes.  
Arquivos afetados: `docs/34-prompt-claude-code.md`, `README.md`.  
Proximo passo: Usar o prompt ao iniciar sessoes de desenvolvimento.

## DEC-0006

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: SUPERADA PARCIALMENTE pela DEC-0012
Contexto: A camada de inteligencia precisa de um provedor de IA padrao.  
Decisao: Adotar Claude (Anthropic) como provedor de IA padrao, dentro de uma camada configuravel (`AI_PROVIDER`).  
Motivo: Forte raciocinio administrativo/juridico e baixa alucinacao para resumos e minutas fieis.  
Impacto: A futura `app/intelligence/` usara cliente Claude; guard e permissoes continuam sendo a barreira final, nunca o prompt. IDs Gemini do `.env.example` devem ser ignorados/corrigidos se houver uso futuro.  
Risco: Dependencia de API externa; mitigada por camada configuravel e proibicao de conteudo vivo do SEI em IA externa (DEC-0003).  
Arquivos afetados: `.env.example`, `docs/26`, `docs/33`.  
Proximo passo: Nao implementar cliente pago por padrao. A DEC-0012 determina custo zero; priorizar regras locais, templates, OCR gratuito e modelo local opcional.

## DEC-0007

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: A criacao de eventos pode gerar duplicidade com a agenda real existente.  
Decisao: Usar o feed iCal privado (somente leitura) para checar duplicidade antes de criar/simular evento, mantendo `CALENDAR_BACKEND=dry_run` por enquanto.  
Motivo: Evitar eventos duplicados sem precisar de escrita; o ICS nao cria, nao altera e nao convida.  
Impacto: `agenda_service` consulta o ICS; equivalencia por titulo, data, hora, local e numero do processo. Falha de acesso ou ICS ausente tem fallback seguro (nao bloqueia).  
Risco: URL do ICS e segredo; tratada apenas no `.env`, nunca versionada/logada.  
Arquivos afetados: `app/integrations/ics_reader.py`, `app/integrations/agenda_service.py`, `.env.example`, `.gitignore`.  
Proximo passo: Apos OAuth, cruzar dedup ICS com criacao real.

## DEC-0008

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: Para criar eventos reais e convidar Oficiais e preciso autenticar no Google.  
Decisao: Usar credencial OAuth "Desktop app" com escopos minimos `calendar.events` e `contacts.readonly`; o agente nunca guarda senha, apenas o refresh token no `.env` local. Sem credenciais completas, o sistema permanece em dry-run.  
Motivo: Menor privilegio, sem conta de servico ampla, preservando seguranca.  
Impacto: Responsavel roda consentimento uma vez (`google_oauth_setup.py`); `runtime` liga o backend real automaticamente quando ha credenciais e `CALENDAR_BACKEND=google`.  
Risco: Refresh token e segredo; em app "Testing" expira em 7 dias (mitigar publicando o app).  
Arquivos afetados: `app/integrations/google_auth.py`, `app/integrations/runtime.py`, `scripts/google_oauth_setup.py`, `.env.example`, `.gitignore`.  
Proximo passo: Concluir consentimento e validar com `google_validate.py`.

## DEC-0009

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O grupo "OFICIAIS" e um marcador do Google Contatos com contatos individuais, nao um e-mail de grupo.  
Decisao: Resolver os convidados a partir do marcador `OFICIAIS` via People API (`OFFICERS_SOURCE=google_contacts`), extraindo os e-mails individuais; `OFFICERS_GROUP_EMAIL` deixa de ser obrigatorio.  
Motivo: Refletir a realidade do cadastro e permitir convite individual rastreavel.  
Impacto: Sem e-mails resolvidos, nao cria evento de convocacao; auditoria registra somente a quantidade de convidados, nunca os e-mails.  
Risco: Depende de credenciais People API; em dry-run usa lista estatica para simular.  
Arquivos afetados: `app/integrations/contacts_resolver.py`, `app/integrations/agenda_service.py`, `.env.example`.  
Proximo passo: Validar contagem real de Oficiais apos OAuth.

## DEC-0010

Data: 2026-06-22
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O chefe do projeto esclareceu que o agente precisa interagir na propria tela do SEI, pois uma tela separada tende a cair em desuso.
Decisao: Priorizar um prototipo de extensao de navegador read-only dentro da tela do SEI, com botao flutuante e painel lateral, conectado ao backend local.
Motivo: Aumentar aderencia operacional, mantendo o servidor no fluxo real de trabalho do SEI.
Impacto: O painel local continua como backend/API, mas a experiencia principal passa a ser o assistente visual na pagina do SEI.
Risco: Leitura direta da tela do SEI e sensivel; mitigacao por modo read-only, sem cookies, sem senha, sem clique automatico, sem busca/navegacao por numero e sem atos oficiais.
Arquivos afetados: `browser_extension/`, `docs/22`, `docs/26`, `docs/27`, `docs/33`, `docs/35`.
Proximo passo: Homologar extensao local read-only com usuario autenticado manualmente no SEI.

## DEC-0011

Data: 2026-06-22
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O ambiente institucional pode bloquear extensoes Chrome/Edge. Foi levantada a possibilidade de abrir o Agente 19 com login e senha do SEI dentro dele.
Decisao: Criar a Fase 37.2 - Agente 19 Desktop com Navegador Seguro, recusando qualquer captura de usuario, senha, cookie, sessao, token, localStorage, sessionStorage ou header de autenticacao do SEI.
Motivo: Manter o Agente 19 util mesmo sem extensao, sem transformar o sistema em intermediario de credenciais do SEI.
Impacto: O login ocorre exclusivamente na pagina oficial `https://sei.go.gov.br/sei/`; o Agente 19 roda em janela local, fala apenas com `127.0.0.1` e recebe texto/PDF fornecido manualmente pelo usuario.
Risco: Uso com navegador interno ou janela separada ainda precisa de homologacao/autorizacao institucional antes de producao real.
Arquivos afetados: `app/desktop/`, `tests/test_desktop_secure_browser.py`, `docs/27`, `docs/33`, `docs/36`, `docs/37`.
Proximo passo: Homologar o desktop com exemplos anonimizados e confirmar se o SEI deve abrir em navegador separado ou WebView institucional.

## DEC-0012

Data: 2026-06-22
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O chefe do projeto informou que nao ha orcamento para pagar por qualquer servico.
Decisao: O Agente 19 deve seguir estrategia zero custo por padrao: sem API paga, sem assinatura, sem ferramenta RPA paga, sem hospedagem paga e sem dependencia financeira.
Motivo: Tornar o projeto viavel na realidade operacional atual.
Impacto: IA externa paga deixa de ser caminho padrao; priorizar regras locais, templates, SQLite, PDF/OCR gratuito, desktop local e eventual modelo local gratuito se houver hardware/autorizacao.
Risco: Analises podem ser menos sofisticadas que modelos pagos; mitigacao por knowledge base real, templates bem feitos, revisao humana e evolucao incremental.
Arquivos afetados: `docs/27`, `docs/30`, `docs/33`, `docs/36`, `docs/38`.
Proximo passo: Implementar minutador por templates locais antes de qualquer IA paga ou integracao onerosa.

## DEC-0013

Data: 2026-06-22
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: A proxima fase apos a estrategia zero custo e gerar minutas administrativas sem contratar servico de IA.
Decisao: Implementar minutador local por regras e templates, com tipos despacho, oficio, informacao e encaminhamento.
Motivo: Entregar valor operacional imediato, mantendo custo zero e revisao humana.
Impacto: O Agente 19 passa a gerar rascunhos copiaveis fora do SEI, sem criar documento oficial, sem assinar, sem tramitar e sem enviar processo.
Risco: Classificacao por regras pode ter baixa confianca; mitigacao por placeholders, alertas e revisao humana obrigatoria.
Arquivos afetados: `app/intelligence/local_minutador.py`, `knowledge_base/templates_minutas/`, `app/dashboard/local_app.py`, `app/desktop/secure_browser.py`, `tests/test_local_minutador.py`, `docs/39`.
Proximo passo: Preencher knowledge base real do 19 CRPM e melhorar regras de classificacao/roteamento.

## DEC-0014

Data: 2026-06-22
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: Para melhorar triagem, roteamento e escolha de minuta sem IA paga, o projeto precisa de regras locais do 19 CRPM.
Decisao: Criar knowledge base local em CSV/Markdown e motor de triagem por regras. Sem regra real clara, retornar `indefinido` e exigir revisao humana.
Motivo: Evitar invencao de unidade responsavel e manter custo zero.
Impacto: O Agente 19 passa a ter endpoint de triagem local e botoes no painel/desktop, mas ainda depende de preenchimento real da base para operar com maior confianca.
Risco: Base vazia ou incompleta gera baixa utilidade; mitigacao por campos pendentes, baixa confianca e revisao obrigatoria.
Arquivos afetados: `knowledge_base/fluxos_19crpm/`, `app/intelligence/knowledge_base.py`, `app/intelligence/local_triage.py`, `tests/test_local_knowledge_base.py`, `docs/40`.
Proximo passo: Preencher unidades e regras reais do 19 CRPM com revisao do responsavel.

## DEC-0015

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O projeto nao possui API oficial, WSSEI, modulo oficial SEI IA ou acesso da TI. O uso previsto e particular/local, com login manual do usuario no SEI Goias.
Decisao: Reenquadrar o projeto como Agente SEI Inteligente Particular, assistente local supervisionado para analise de processos, geracao de minutas e apoio operacional no SEI.
Motivo: Permitir evolucao util sem capturar credenciais, sem depender de autorizacao tecnica inexistente e sem automatizar ato oficial.
Impacto: O LLM nao controla navegador; o LLM apenas analisa texto, classifica, sugere providencia e gera conteudo. Qualquer interacao com SEI deve ser codigo deterministico, auditado, com allow-list/default-deny, chokepoint de leitura, `ReadOnlyPage`, sessao efemera e feature flags desligadas por padrao.
Risco: Confundir minuta controlada com escrita real pronta; mitigacao por FASE 5A simulada, `ENABLE_MINUTA_CREATION=false`, stubs `NotImplementedError` e FASE 5B futura dependente de homologacao.
Arquivos afetados: `README.md`, `.env.example`, `docs/01`, `docs/02`, `docs/06`, `docs/08`, `docs/27`, `docs/33`, `docs/35`, `docs/36`, `docs/fase-5-minuta-controlada.md`.
Proximo passo: PATCH 4 registrado na DEC-0016.

## DEC-0016

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O PATCH 1/3 + 2/3 + 3/3 foi aprovado para FASE 5A com a condicao de nao habilitar escrita real no SEI.
Decisao: Aplicar PATCH 4 de hardening final antes de qualquer merge para `main`.
Motivo: Impedir ativacao insegura em producao, garantir auditoria por hash e bloquear uso direto de Playwright fora do arquivo autorizado.
Impacto: Startup valida `assert_safe_environment()`; `MINUTA_TOKEN_SECRET` padrao/curto e `ENABLE_MINUTA_CREATION=true` sao bloqueados em producao; `MinutaWriter` audita `text_hash`; escrita real permanece `NotImplementedError`.
Risco: FASE 5B ainda nao existe; mitigacao por flags desligadas, teste arquitetural e documentacao de que a escrita real nao esta pronta.
Arquivos afetados: `app/core/config.py`, `app/core/safety.py`, `app/dashboard/local_app.py`, `app/desktop/secure_browser.py`, `app/sei/minuta_token.py`, `app/sei/read_only_page.py`, `app/sei/playwright_session.py`, `app/sei/minuta_writer.py`, `tests/test_phase5a_minuta_controlada.py`, docs vivos.
Proximo passo: Preparar FASE 5B somente em homologacao com seletores reais validados e nivel de acesso explicito.

## DEC-0017

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: Apos o PATCH 4, a proxima fase deve preparar a FASE 5B sem habilitar escrita real no SEI.
Decisao: Criar FASE 5B-homologacao com contrato de cadastro, nivel de acesso obrigatorio, manifesto de seletores e avaliador de prontidao.
Motivo: Permitir homologacao controlada dos seletores reais antes de qualquer tentativa de escrita no SEI.
Impacto: O projeto passa a validar tipo documental, nivel de acesso, hipotese legal quando necessario, campos administrativos aplicaveis e seletores homologados. Mesmo com tudo valido, `real_write_allowed=false`.
Risco: Confundir prontidao para homologacao com autorizacao para escrita real; mitigacao por template sem seletores reais, bloqueio de seletores de atos oficiais e escrita real ainda ausente.
Arquivos afetados: `app/sei/minuta_cadastro.py`, `app/sei/selector_manifest.py`, `app/sei/fase5b_homologacao.py`, `knowledge_base/sei_homologacao/minuta_selectors.template.json`, `tests/test_phase5b_homologacao.py`, docs vivos.
Proximo passo: Preencher manifesto somente em homologacao controlada, com evidencia, sem assinar/tramitar/enviar/concluir.

## DEC-0018

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: Foi solicitado pesquisar no GitHub se ha API SEI disponivel sem acionar a TI. A pesquisa indicou `mod-wssei` como melhor pista tecnica, mas dependente de estar ativo/autorizado na instancia.
Decisao: Criar diagnostico seguro local para verificar endpoints candidatos sem autenticar e sem enviar credenciais.
Motivo: Permitir evidencia tecnica inicial sem capturar senha, cookie, token ou sessao e sem praticar operacao de negocio.
Impacto: O projeto passa a ter `scripts/sei_api_discovery.py` e `app/sei/api_discovery.py` para testar candidatos `mod-wssei-v2`, `mod-wssei-v1` e WSDL nativo.
Risco: Interpretar endpoint existente como autorizacao de uso; mitigacao por classificacao conservadora e documentacao de que resultado positivo nao libera uso real.
Arquivos afetados: `app/sei/api_discovery.py`, `scripts/sei_api_discovery.py`, `tests/test_sei_api_discovery.py`, `docs/41-diagnostico-api-sei-wssei.md`, docs vivos.
Proximo passo: Rodar diagnostico e registrar resultado em `docs/32-registro-testes-homologacao.md`.

## DEC-0019

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O diagnostico seguro foi executado contra `https://sei.go.gov.br/sei/` sem credenciais.
Decisao: Nao adotar API SEI/WSSEI como caminho imediato, pois os caminhos publicos padrao nao retornaram endpoint utilizavel.
Motivo: `mod-wssei-v2` e `mod-wssei-v1` retornaram 404; WSDL nativo ficou indisponivel com conexao encerrada pelo host remoto.
Impacto: O projeto continua no caminho local supervisionado, com login manual, leitura assistida, minuta local/controlada e FASE 5B apenas em homologacao.
Risco: Pode existir endpoint interno nao publico; mitigacao por manter a possibilidade documentada, mas exigir autorizacao/informacao oficial antes de qualquer uso real.
Arquivos afetados: `docs/42-resultado-diagnostico-real-api-sei.md`, `scripts/sei_api_discovery.py`, `app/sei/api_discovery.py`, docs vivos.
Proximo passo: Continuar desenvolvimento local supervisionado; API real somente se houver endpoint autorizado.

## DEC-0020

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: O usuario definiu que o Agente 19 deve ficar na tela do SEI em formato de chat, com visual profissional e inovador.
Decisao: Adotar UI principal como chat lateral flutuante na extensao read-only.
Motivo: Aproximar o agente da rotina real do SEI e permitir interacao natural enquanto o usuario esta logado manualmente.
Impacto: A extensao passa a ter botao flutuante compacto, historico de mensagens, campo de pergunta e acoes rapidas de resumo, prazo e providencia.
Risco: Confundir chat com automacao oficial; mitigacao por aviso fixo, modo read-only, ausencia de clique automatico e backend local.
Arquivos afetados: `browser_extension/content.js`, `browser_extension/content.css`, `browser_extension/manifest.json`, `tests/test_browser_extension_contract.py`, `docs/43-ui-chat-agente19-sei.md`.
Proximo passo: Homologar visualmente a extensao com SEI aberto, usando caso anonimizado ou nao sensivel.

## DEC-0021

Data: 2026-06-23
Responsavel: Chefe do projeto
Status: APROVADA
Contexto: A UI em formato de chat precisa apoiar geracao de minutas sem parecer que o agente escreve ou cria documentos no SEI.
Decisao: A acao `Minuta` na UI chat gera somente rascunho externo supervisionado, com status visivel de somente leitura, backend local e revisao humana.
Motivo: Entregar valor operacional dentro da tela do SEI sem praticar ato oficial, sem clicar na pagina e sem ultrapassar a FASE 5A/5B-homologacao.
Impacto: O chat passa a exibir status operacional, atalho `Esc`, acao `Minuta` e resposta formatada como rascunho externo copiavel.
Risco: Usuario interpretar rascunho como documento oficial; mitigacao por texto fixo informando que a insercao no SEI permanece manual e exige conferencia humana.
Arquivos afetados: `browser_extension/content.js`, `browser_extension/content.css`, `browser_extension/manifest.json`, `browser_extension/preview_chat.html`, `tests/test_browser_extension_contract.py`, `docs/45-ux-chat-v2-minuta-externa.md`.
Proximo passo: Homologar visualmente a UI V2 no preview local antes de testar no SEI real autorizado.
