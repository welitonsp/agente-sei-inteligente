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
