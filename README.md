# Agente SEI Inteligente - 19 CRPM

Documentacao-base do projeto de um agente administrativo inteligente para apoiar a rotina do 19 CRPM com e-mail institucional, PDF, Google Agenda, alertas em celular, minutas administrativas e uso assistido do SEI.

Versao documental: 0.3.1
Data: 2026-06-22
Status: Fundacao tecnica + Agenda dry-run + painel local de texto manual

## Objetivo

Construir uma plataforma web de automacao administrativa assistida. O agente deve transformar demandas recebidas por e-mail, documentos, PDFs e futuramente pelo SEI em tarefas organizadas: resumo, classificacao, prazo, evento de agenda, alerta, minuta e pendencia para revisao humana.

O sistema prepara, organiza e sugere. Ele nao substitui a autoridade humana, nao assina documento, nao tramita processo, nao envia processo e nao conclui ato oficial no SEI.

## Principios

1. Humano no controle dos atos oficiais.
2. Seguranca antes de automacao.
3. Baixo custo e dependencia minima de servicos pagos.
4. Modulos independentes e testaveis.
5. Logs e rastreabilidade de todas as acoes.
6. Interface principal pensada para web e celular.
7. Integracao com SEI somente em modo assistido e progressivo.

## Escopo da versao 1

A versao 1 sera considerada pronta quando o agente conseguir:

1. Ler e-mail institucional.
2. Ler anexos PDF pesquisaveis.
3. Identificar evento, prazo, assunto, origem e providencia.
4. Criar evento no Google Agenda.
5. Adicionar automaticamente o grupo de Oficiais.
6. Enviar convite de agenda.
7. Alertar no celular, inicialmente via Telegram.
8. Gerar resumo e minuta administrativa.
9. Registrar logs e evitar duplicidade.
10. Bloquear atos oficiais no SEI.

## Documentacao

| Arquivo | Conteudo |
| --- | --- |
| [docs/00-visao-geral.md](docs/00-visao-geral.md) | Visao do produto, problema, usuarios e escopo |
| [docs/01-arquitetura.md](docs/01-arquitetura.md) | Modulos, fluxo tecnico, web app e agentes |
| [docs/02-regras-de-seguranca.md](docs/02-regras-de-seguranca.md) | Permissoes, acoes proibidas e guardas |
| [docs/03-manual-operacional.md](docs/03-manual-operacional.md) | Como operar o agente na rotina administrativa |
| [docs/04-google-agenda.md](docs/04-google-agenda.md) | Padrao de eventos, observacoes, convidados e duplicidade |
| [docs/05-alertas-celular.md](docs/05-alertas-celular.md) | Telegram, e-mail, WhatsApp futuro e modelo de alerta |
| [docs/06-integracao-sei.md](docs/06-integracao-sei.md) | Integracao assistida com SEI e limites de automacao |
| [docs/07-modelos-de-minutas.md](docs/07-modelos-de-minutas.md) | Modelos iniciais de minutas administrativas |
| [docs/08-roadmap.md](docs/08-roadmap.md) | Etapas de evolucao do projeto |
| [docs/09-interface-web.md](docs/09-interface-web.md) | Painel web, telas, estados e controles |
| [docs/10-agentes-ia.md](docs/10-agentes-ia.md) | Desenho dos agentes de IA, ferramentas e decisoes |
| [docs/11-modelo-de-dados.md](docs/11-modelo-de-dados.md) | Entidades, tabelas, logs e retencao |
| [docs/12-backlog-e-criterios.md](docs/12-backlog-e-criterios.md) | Backlog priorizado e criterios de aceite |
| [docs/13-perguntas-pendentes.md](docs/13-perguntas-pendentes.md) | Decisoes que ainda precisam de confirmacao |
| [docs/14-api-e-tarefas.md](docs/14-api-e-tarefas.md) | Contratos para a pagina web executar tarefas |
| [docs/15-governanca-e-riscos.md](docs/15-governanca-e-riscos.md) | Papeis, decisoes, riscos e mitigacoes |
| [docs/16-plano-de-testes.md](docs/16-plano-de-testes.md) | Estrategia de testes dos modulos e agentes |
| [docs/17-leitura-manuais-sei.md](docs/17-leitura-manuais-sei.md) | Aprendizado extraido dos manuais SEI locais |
| [docs/18-orientacao-gemini-rag.md](docs/18-orientacao-gemini-rag.md) | Como usar Gemini como biblioteca auxiliar do agente |
| [docs/19-pesquisa-agentes-sei-ia.md](docs/19-pesquisa-agentes-sei-ia.md) | Pesquisa na internet sobre SEI IA, ANIA e ferramentas similares |
| [docs/20-politica-identidade-sessao-sei.md](docs/20-politica-identidade-sessao-sei.md) | Politica de usuario, senha, sessao e rastreabilidade no SEI |
| [docs/21-estrategia-sem-modulo-oficial-sei.md](docs/21-estrategia-sem-modulo-oficial-sei.md) | Estrategia adotada sem instalacao do modulo oficial SEI IA |
| [docs/22-robozinho-sei-assistente.md](docs/22-robozinho-sei-assistente.md) | Requisito do assistente visual na tela do SEI |
| [docs/23-skills-especialistas.md](docs/23-skills-especialistas.md) | Skills especialistas do Agente SEI |
| [docs/24-contratos-das-skills.md](docs/24-contratos-das-skills.md) | Entradas, saidas e validacoes de cada skill |
| [docs/25-politica-dados-sei.md](docs/25-politica-dados-sei.md) | Politica para textos, PDFs e dados extraidos do SEI |
| [docs/26-matriz-conformidade.md](docs/26-matriz-conformidade.md) | Conformidades, nao conformidades e liberacao por fase |
| [docs/27-checklist-processos-desenvolvimento.md](docs/27-checklist-processos-desenvolvimento.md) | Checklist de processos para desenvolvimento |
| [docs/28-regras-git-ia.md](docs/28-regras-git-ia.md) | Regras de commit, push, PR e merge com uso de IA |
| [docs/29-regra-documentacao-continua.md](docs/29-regra-documentacao-continua.md) | Regra para documentar processos, decisoes e mudancas continuamente |
| [docs/30-registro-decisoes.md](docs/30-registro-decisoes.md) | Registro oficial de decisoes (DEC-XXXX) |
| [docs/31-registro-processos.md](docs/31-registro-processos.md) | Registro de processos internos (PROC-XXXX) |
| [docs/32-registro-testes-homologacao.md](docs/32-registro-testes-homologacao.md) | Registro de testes e homologacao (TEST-XXXX) |
| [docs/33-changelog.md](docs/33-changelog.md) | Changelog das entregas |
| [docs/34-prompt-claude-code.md](docs/34-prompt-claude-code.md) | Prompt mestre para Claude Code executar o projeto |
| [docs/35-handoff-retomada.md](docs/35-handoff-retomada.md) | Handoff: ponto de parada e como retomar em outra estacao |

## Estrutura-alvo

```text
agente-sei-inteligente/
├── README.md
├── .env.example
├── docs/
├── app/
│   ├── core/
│   ├── intake/
│   ├── intelligence/
│   ├── integrations/
│   ├── sei/
│   ├── storage/
│   ├── workers/
│   └── dashboard/
├── knowledge_base/
├── tests/
└── scripts/
```

## Stack recomendada

| Camada | Opcao inicial |
| --- | --- |
| Backend | Python com FastAPI |
| Interface web | Streamlit para MVP ou React/Next.js para produto final |
| Banco inicial | SQLite |
| Banco futuro | PostgreSQL |
| Fila simples | APScheduler ou RQ |
| PDF | PyMuPDF ou pdfplumber |
| E-mail | IMAP, Gmail API ou Microsoft Graph, conforme conta institucional |
| Agenda | Google Calendar API |
| Alertas | Telegram Bot API |
| Automacao web assistida | Playwright, sempre protegido por guarda de acoes |
| IA | Provedor configuravel, com opcao local ou API externa |

## Regra de ouro

Nenhuma acao oficial no SEI pode ser automatizada sem revisao e comando humano direto. O agente pode ler, resumir, classificar, preparar minuta e registrar pendencia. Assinatura, envio, tramitacao, conclusao, ciencia automatica, cancelamento e exclusao ficam proibidos.

## Decisao atual sobre SEI

Como nao ha viabilidade de instalar o modulo oficial SEI IA no ambiente institucional, o projeto adotara arquitetura externa/local assistida. O agente nao sera instalado dentro do SEI, nao usara usuario unico e nao guardara credenciais. Cada servidor continuara acessando o SEI com sua propria conta, em sua propria estacao, e o agente apenas auxiliara leitura, resumo, agenda, alertas e minutas.

## Robozinho na tela do SEI

O produto desejado tera um assistente visual acionado pelo servidor durante o uso do SEI. Sem modulo oficial, esse recurso devera ser implementado como extensao de navegador, painel lateral local ou sobreposicao autorizada na estacao de trabalho. O servidor loga no SEI normalmente, clica no robozinho, informa o numero do processo e o agente le somente o que a sessao daquele servidor permite visualizar.

O robozinho deve ajudar a identificar o que interessa ao 19 CRPM, explicar o conteudo, apontar prazo, finalidade, unidade responsavel e minuta/arquivo sugerido, sem assinar, enviar, tramitar, concluir, dar ciencia ou alterar qualquer ato oficial no SEI.

Regra de credencial: o login deve ser feito pelo usuario individual do servidor. O agente nao deve guardar nem digitar senha; ele apenas atua depois que o servidor autenticou sua propria sessao.

Regra de leitura: no MVP, o servidor deve abrir o processo/documento no SEI ou fornecer texto/PDF ao agente. Informar o numero do processo serve para identificar e conferir a analise; nao autoriza o agente a pesquisar, navegar ou clicar sozinho no SEI.
