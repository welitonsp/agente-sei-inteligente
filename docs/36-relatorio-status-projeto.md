# Relatorio de status do projeto

Data: 2026-06-23
Branch: `feat/fundacao-agenda-ics`
PR: https://github.com/welitonsp/agente-sei-inteligente/pull/1
Status geral: fundacao tecnica, painel local, intake texto/PDF, Agente 19 Desktop seguro, estrategia zero custo, minutador local zero custo, knowledge base local 19 CRPM, UI chat V2 da extensao SEI read-only, novo enquadramento arquitetural particular/local, PATCH 4 de hardening da FASE 5A, FASE 5B-homologacao e diagnostico seguro de API SEI/WSSEI implementados. Operacao real ainda depende de homologacao e autorizacoes.

## 1. Resumo executivo

O projeto ja possui uma base tecnica segura para operar como assistente administrativo do 19 CRPM. O sistema ainda nao esta liberado para operacao real com dados sensiveis, mas ja consegue receber texto/PDF fornecido pelo usuario, gerar analise estruturada basica, registrar auditoria sem salvar texto integral, simular integracao com agenda, abrir o Agente 19 como desktop local seguro e aparecer dentro da tela do SEI por uma extensao read-only quando autorizada.

Formato de UI definido: o Agente 19 na tela do SEI sera um chat lateral
flutuante, profissional, com campo de pergunta, historico de mensagens, status
operacional visivel e acoes rapidas de resumo, prazos, providencia e minuta
externa supervisionada. Tambem existe preview local em
`browser_extension/preview_chat.html` para avaliacao visual sem SEI real.

Regra principal mantida: o sistema ajuda, organiza e sugere. Atos oficiais no SEI continuam manuais e sob responsabilidade do servidor logado.

Restricao financeira permanente: o projeto deve operar com custo zero por
padrao, sem API paga, assinatura, RPA pago ou hospedagem paga.

Enquadramento SEI atualizado: o projeto e uma solucao particular/local. O usuario
faz login manualmente no SEI Goias; o agente nao guarda senha, nao captura
cookie/token/sessao, nao persiste perfil do navegador e nao permite que o LLM
controle o navegador. Interacoes com SEI devem ser codigo deterministico,
auditado e protegido por allow-list/default-deny.

FASE 5A: minuta controlada simulada com PATCH 4 aplicado. A escrita real no SEI
ainda NAO esta habilitada. A FASE 5B futura, se homologada, deve limitar-se a
criar uma minuta usando um tipo de documento ja existente no SEI, salvar e parar.

FASE 5B-homologacao: contratos de cadastro, nivel de acesso e manifesto de
seletores foram preparados. Mesmo quando o avaliador indicar prontidao para
homologacao, `real_write_allowed=false`.

Diagnostico API SEI/WSSEI: executado contra `https://sei.go.gov.br/sei/` sem
enviar usuario, senha, cookie, token ou sessao. `mod-wssei-v2` e `mod-wssei-v1`
retornaram 404; WSDL nativo ficou indisponivel com conexao encerrada pelo host
remoto.

## 2. Checklist do que ja foi executado

### Governanca e documentacao

- [x] Repositorio GitHub criado: `welitonsp/agente-sei-inteligente`.
- [x] Documentacao base criada em `docs/00` a `docs/36`.
- [x] Matriz de conformidade criada.
- [x] Regras de seguranca, dados, identidade e uso do SEI documentadas.
- [x] Registro de decisoes criado.
- [x] Registro de processos criado.
- [x] Registro de testes/homologacao criado.
- [x] Changelog criado e atualizado.
- [x] Handoff de retomada criado.
- [x] Relatorio de status consolidado criado neste arquivo.
- [x] Fase 37.2 documentada em `docs/37-fase-desktop-navegador-seguro.md`.
- [x] Estrategia zero custo documentada em `docs/38-estrategia-zero-custo-sei.md`.
- [x] Novo enquadramento SEI particular/local documentado no README.
- [x] FASE 5 documentada em `docs/fase-5-minuta-controlada.md`.

### Fundacao tecnica e seguranca

- [x] Estrutura inicial `app/` criada.
- [x] Configuracao central criada em `app/core/config.py`.
- [x] Lista de permissoes criada em `app/core/permissions.py`.
- [x] Guardiao de acoes do SEI criado em `app/sei/sei_action_guard.py`.
- [x] Bloqueio por padrao para acoes nao autorizadas.
- [x] Acoes oficiais proibidas mapeadas e testadas.
- [x] Filtro de seguranca criado para sanitizar segredos.
- [x] Logging estruturado criado.
- [x] Auditoria criada.
- [x] Testes automatizados para permissoes, guardiao, auditoria e filtro de seguranca.

### Banco de dados e auditoria

- [x] Banco SQLite inicial criado.
- [x] Modelos iniciais implementados em `app/storage/models.py`.
- [x] Script de inicializacao do banco criado: `scripts/init_db.py`.
- [x] Entidades de processo, documento, evento, alerta e auditoria estruturadas.
- [x] Hash/metadados registrados sem persistir texto integral por padrao.

### CI, qualidade e segredos

- [x] GitHub Actions criado em `.github/workflows/ci.yml`.
- [x] Pipeline roda em Python 3.11 e 3.13.
- [x] Scanner de segredos criado em `scripts/check_no_secrets.py`.
- [x] Scanner bloqueia `.env`, tokens, client secrets, URL ICS e chaves concretas.
- [x] Suite automatizada com 150 testes passando.
- [x] PR #1 aberto em modo draft.
- [x] Checks remotos aprovados no GitHub Actions.

### Google Agenda

- [x] Servico de agenda criado em modo dry-run.
- [x] Backend em memoria para simulacao criado.
- [x] Backend Google preparado para OAuth.
- [x] Cliente OAuth Calendar + People criado.
- [x] Script para gerar refresh token criado.
- [x] Script de validacao Google criado.
- [x] Resolucao de convidados pelo marcador `OFICIAIS` preparada.
- [x] Leitor ICS read-only criado.
- [x] Deduplicacao local e por calendario ICS criada.
- [x] Criacao de evento real continua bloqueada ate OAuth e revisao humana.

### Intake de texto manual

- [x] Backend `IMPORT_TEXT` criado.
- [x] Recebe texto colado pelo servidor.
- [x] Nao acessa SEI real.
- [x] Gera hash do texto.
- [x] Registra metadados e resumo estrutural.
- [x] Detecta evento/prazo simples por heuristica.
- [x] Exige revisao humana obrigatoria.
- [x] Nao persiste texto integral por padrao.
- [x] Testes automatizados criados.

### Intake de PDF

- [x] Upload local de PDF criado.
- [x] Extracao de texto de PDF pesquisavel com `pypdf`.
- [x] Deteccao de PDF sem texto extraivel.
- [x] Marcacao `ocr_necessario` quando o PDF precisa de OCR.
- [x] Tratamento de PDF invalido.
- [x] Registro de hash, paginas e metadados.
- [x] Texto integral nao e persistido por padrao.
- [x] Testes automatizados criados.

### Painel local

- [x] Painel local criado em `app/dashboard/local_app.py`.
- [x] Executavel com `.venv\Scripts\python.exe -m app.dashboard`.
- [x] Endpoint `POST /api/import-text` criado.
- [x] Endpoint `POST /api/import-pdf` criado.
- [x] Tela com numero do processo SEI.
- [x] Campo de texto copiado do SEI.
- [x] Upload de PDF.
- [x] Botao de analise local.
- [x] Resultado estruturado exibido.
- [x] Indicacao de revisao humana obrigatoria.
- [x] Indicacao de OCR necessario quando aplicavel.

### Agente 19 Desktop seguro

- [x] Aplicacao desktop local criada em `app/desktop/`.
- [x] Comando `.venv\Scripts\python.exe -m app.desktop` criado.
- [x] Backend local iniciado/reutilizado em `127.0.0.1`.
- [x] Botao para abrir o SEI pela URL oficial `https://sei.go.gov.br/sei/`.
- [x] Aviso fixo de que o login ocorre somente na pagina oficial do SEI.
- [x] Painel desktop para texto copiado manualmente.
- [x] Painel desktop para PDF exportado manualmente.
- [x] Resultado com resumo, tipo provavel, evento/prazo e providencia sugerida.
- [x] Botao de copiar resultado.
- [x] Bloqueio de campos/payloads com credenciais.
- [x] Teste automatizado contra campo de senha/login SEI.

### Minutador local zero custo

- [x] Motor local por regras/templates criado.
- [x] Templates locais de despacho, oficio, informacao e encaminhamento criados.
- [x] Endpoint `POST /api/generate-draft` criado.
- [x] Botao de minuta no painel local.
- [x] Botao de minuta no desktop.
- [x] Resultado copiavel.
- [x] Revisao humana obrigatoria.
- [x] Acoes oficiais bloqueadas no contrato.
- [x] Auditoria sem texto integral.

### FASE 5A - minuta controlada simulada

- [x] Arquitetura segura documentada.
- [x] `ENABLE_MINUTA_CREATION=false` registrado como padrao seguro.
- [x] Token de confirmacao definido como requisito.
- [x] Verificacao de processo correto definida como requisito.
- [x] Allow-list separada de escrita controlada definida como requisito.
- [x] Escrita real no SEI mantida como nao habilitada.
- [x] PATCH 4 de hardening final.
- [ ] FASE 5B com seletores homologados.

### FASE 5B-homologacao

- [x] Contrato de cadastro de minuta criado.
- [x] `nivel_acesso` obrigatorio.
- [x] `hipotese_legal` obrigatoria para restrito/sigiloso.
- [x] Manifesto de seletores criado.
- [x] Template sem seletores reais criado.
- [x] Bloqueio de seletores de atos oficiais.
- [x] `real_write_allowed=false`.
- [ ] Preencher manifesto em homologacao controlada.
- [ ] Implementar escrita real com seletores homologados.

### Diagnostico seguro de API SEI/WSSEI

- [x] Montagem de URLs candidatas.
- [x] Diagnostico sem credenciais.
- [x] Bloqueio de URL com credencial.
- [x] Sem Cookie/Authorization/payload.
- [x] Script `scripts/sei_api_discovery.py`.
- [x] Documento da Fase 41.
- [x] Rodar diagnostico real manualmente.
- [x] Registrar resultado na Fase 42.

### Knowledge base local 19 CRPM

- [x] Pasta local `knowledge_base/fluxos_19crpm/` criada.
- [x] Templates de unidades, palavras-chave e regras criados.
- [x] Loader local de CSV criado.
- [x] Triagem/roteamento por regras criado.
- [x] Endpoint `POST /api/triage-local` criado.
- [x] Botao de triagem no painel local.
- [x] Botao de triagem no desktop.
- [x] Sem regra real, retorna `indefinido` e nao inventa unidade.
- [ ] Preencher dados reais do 19 CRPM.
- [ ] Homologar com 5 casos anonimizados.

### Extensao SEI read-only

- [x] Prototipo de extensao Chrome/Edge criado em `browser_extension/`.
- [x] UI definida como chat lateral profissional.
- [x] UI Chat V2 com status `Somente leitura`, `Backend local` e `Revisao humana`.
- [x] Acao `Minuta` gera apenas rascunho externo para conferencia humana.
- [x] Manifest V3 criado.
- [x] Permissao restrita a `https://sei.go.gov.br/sei/*` e `http://127.0.0.1:8000/*`.
- [x] Botao flutuante `Agente 19` aparece dentro da tela do SEI.
- [x] Painel lateral aparece dentro da propria pagina do SEI.
- [x] Captura texto visivel ou texto selecionado.
- [x] Envia conteudo somente ao backend local.
- [x] Nao usa permissao de cookies.
- [x] Nao usa `webRequest`.
- [x] Nao salva senha, cookie ou sessao.
- [x] Nao executa clique automatico.
- [x] Nao submete formularios do SEI.
- [x] Nao executa ato oficial.
- [x] Teste de contrato de seguranca criado.
- [x] Preview local atualizado para simular minuta externa.
- [ ] Homologacao visual da UI chat no SEI real.
- [x] Preview local da UI chat criado.
- [ ] Feedback visual do preview pelo usuario.

## 3. Checklist do que o sistema ja faz hoje

### Operacao local

- [x] Inicializa banco SQLite.
- [x] Roda suite de testes.
- [x] Verifica ausencia de segredos no Git.
- [x] Sobe painel local em `http://127.0.0.1:8000`.
- [x] Recebe texto manual informado pelo usuario.
- [x] Recebe PDF local informado pelo usuario.
- [x] Retorna resultado estruturado para revisao humana.
- [x] Registra auditoria sem expor texto integral.

### Analise administrativa basica

- [x] Identifica numero de processo informado.
- [x] Calcula hash do conteudo.
- [x] Conta caracteres/paginas quando aplicavel.
- [x] Detecta sinais simples de evento.
- [x] Detecta sinais simples de prazo.
- [x] Marca baixa confianca e revisao humana.
- [x] Indica pendencias quando o documento nao pode ser totalmente lido.

### Agenda

- [x] Monta evento em formato padronizado.
- [x] Monta observacao padronizada.
- [x] Prepara lembretes.
- [x] Resolve convidados por marcador `OFICIAIS` quando Google estiver configurado.
- [x] Evita duplicidade local.
- [x] Evita duplicidade consultando ICS read-only.
- [x] Simula criacao de evento em dry-run.

### SEI

- [x] Pode aparecer dentro da tela do SEI por extensao local.
- [x] Pode funcionar sem extensao por aplicacao desktop local.
- [x] Pode abrir o SEI oficial em janela separada, com login feito diretamente na pagina oficial.
- [x] Pode ler texto visivel/selecionado da pagina atual apos acao do usuario.
- [x] Pode enviar esse texto para analise local.
- [x] Mantem atos oficiais manuais.
- [x] Mantem login do SEI sob controle do servidor.
- [x] Nao pesquisa processo automaticamente.
- [x] Nao navega sozinho no SEI.
- [x] Nao clica em botoes do SEI.

## 4. Checklist do que ainda falta executar

### Homologacao e uso real

- [ ] Homologar o painel local com exemplos anonimizados.
- [ ] Homologar o Agente 19 Desktop seguro em ambiente institucional.
- [ ] Definir se o SEI abrira em navegador separado ou WebView institucional homologado.
- [ ] Homologar a extensao read-only na tela real do SEI.
- [ ] Registrar evidencias da homologacao manual.
- [ ] Obter autorizacao institucional para uso real da extensao.
- [ ] Definir politica de instalacao da extensao nas maquinas.
- [ ] Definir se o PR #1 sai de draft para pronto para revisao.
- [ ] Fazer merge na `main` apos revisao humana.
- [ ] Configurar protecao da branch `main`.

### Google Agenda real

- [ ] Publicar o app OAuth ou adicionar `19crpm.pm@gmail.com` como test user.
- [ ] Inserir `GOOGLE_CLIENT_SECRET` no `.env` local.
- [ ] Rodar `scripts/google_oauth_setup.py`.
- [ ] Obter e salvar `GOOGLE_REFRESH_TOKEN` no `.env` local.
- [ ] Rodar `scripts/google_validate.py`.
- [ ] Fazer primeiro evento real de teste com revisao humana.
- [ ] Registrar homologacao do evento real.

### Dados reais do 19 CRPM

- [ ] Preencher unidades reais do 19 CRPM.
- [ ] Preencher unidades de Alto Comando relevantes.
- [ ] Preencher regras reais de direcionamento.
- [ ] Preencher palavras-chave reais por assunto.
- [ ] Preencher modelos de resposta/minuta aprovados.
- [ ] Criar pelo menos 5 casos de teste anonimizados.
- [ ] Definir o que exatamente significa "criar arquivo".

### Skills administrativas

- [ ] Implementar `sei-leitor-readonly`.
- [ ] Implementar `resumidor-administrativo`.
- [ ] Implementar `extrator-prazos`.
- [ ] Implementar `extrator-eventos`.
- [ ] Implementar `guardiao-seguranca-sei` como skill operacional.
- [ ] Implementar `auditor-processos`.
- [ ] Implementar `triagem-19crpm` somente depois da knowledge base real.
- [ ] Implementar `roteador-unidades-19crpm` somente depois das regras reais.
- [ ] Garantir saida JSON, confianca, fontes e revisao humana em todas as skills.

### OCR e documentos

- [ ] Implementar OCR real para PDFs escaneados.
- [ ] Validar OCR com PDFs anonimizados.
- [ ] Marcar documento como lido/parcial/nao lido com mais precisao.
- [ ] Criar fluxo para varios documentos no mesmo processo.
- [ ] Criar inventario visual de documentos analisados.

### IA/RAG

- [ ] Definir provedor IA permitido para conteudo nao sensivel.
- [ ] Definir se havera modelo local para conteudo vivo do SEI.
- [ ] Criar retriever para manuais e base autorizada.
- [ ] Criar prompts por skill.
- [ ] Criar logs/tracing sanitizados.
- [ ] Criar avaliacao de fidelidade e ausencia de invencao.
- [ ] Bloquear conteudo real do SEI em IA externa sem autorizacao formal.

### Telegram e alertas

- [ ] Criar bot Telegram.
- [ ] Definir chat/grupo oficial.
- [ ] Implementar servico Telegram.
- [ ] Enviar alerta informativo.
- [ ] Enviar alerta urgente.
- [ ] Registrar envio e falha.
- [ ] Garantir que alertas nao contenham documento completo.

### E-mail institucional

- [ ] Definir provedor de e-mail institucional.
- [ ] Definir modo de acesso: IMAP, Gmail API ou Microsoft Graph.
- [ ] Implementar leitura controlada de e-mails.
- [ ] Extrair anexos.
- [ ] Evitar duplicidade de demandas.
- [ ] Criar trilha de auditoria.

### Interface e produto

- [ ] Criar autenticacao local do painel.
- [ ] Definir perfis de usuario.
- [ ] Melhorar telas operacionais.
- [ ] Criar fila/kanban de pendencias.
- [ ] Criar tela de revisao antes de qualquer acao externa.
- [ ] Criar exportacao de relatorio/minuta fora do SEI.
- [ ] Preparar futura interface mais completa, se necessario.

### Qualidade

- [ ] Adicionar lint/format.
- [ ] Adicionar cobertura de testes, se decidido.
- [ ] Criar testes end-to-end locais do painel.
- [ ] Criar teste manual documentado do desktop.
- [ ] Criar teste manual documentado da extensao.
- [ ] Criar politica de versao e releases.

### Estrategia zero custo

- [x] Implementar minutador por templates locais.
- [x] Criar templates locais de oficio, despacho, informacao e encaminhamento.
- [x] Criar classificacao por regras antes de IA paga.
- [ ] Avaliar OCR gratuito/local.
- [ ] Avaliar modelo local gratuito somente se houver hardware/autorizacao.
- [ ] Manter IA externa paga fora do caminho padrao.

## 5. O que continua proibido

- [ ] Automatizar login no SEI.
- [ ] Pedir usuario ou senha do SEI dentro do Agente 19.
- [ ] Digitar usuario ou senha do servidor.
- [ ] Guardar senha, cookie, token ou sessao do SEI.
- [ ] Ler localStorage/sessionStorage ou headers de autenticacao do SEI.
- [ ] Pesquisar processo automaticamente pelo numero no SEI.
- [ ] Navegar sozinho no SEI.
- [ ] Clicar em botoes do SEI.
- [ ] Assinar documento.
- [ ] Enviar processo.
- [ ] Tramitar processo.
- [ ] Concluir processo.
- [ ] Dar ciencia automaticamente.
- [ ] Excluir ou cancelar documento.
- [ ] Alterar sigilo/acesso.
- [ ] Enviar conteudo real do SEI para IA externa sem autorizacao formal.

## 6. Proxima fase recomendada

1. Testar o Agente 19 Desktop com SEI aberto pela URL oficial, usando somente caso anonimizado ou conteudo nao sensivel.
2. Registrar o resultado em `docs/32-registro-testes-homologacao.md`.
3. Homologar minutas com exemplos anonimizados do 19 CRPM.
4. Preencher os CSVs reais da knowledge base do 19 CRPM.
5. Homologar triagem/roteamento com 5 casos anonimizados.
6. Implementar OCR gratuito/local ou autenticacao local do painel, conforme prioridade operacional.
7. Concluir o OAuth Google e validar agenda real em modo controlado, apenas se usar recursos gratuitos/institucionais ja existentes.
8. Manter a extensao Chrome/Edge como recurso futuro opcional, dependente de autorizacao institucional.
9. Continuar caminho local supervisionado; API real somente se houver endpoint autorizado/informacao oficial.

## 7. Como testar o que ja existe

```bat
.venv\Scripts\python.exe scripts\check_no_secrets.py .
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m app.desktop
.venv\Scripts\python.exe -m app.dashboard
```

Depois abrir:

```text
http://127.0.0.1:8000
```

Para a extensao:

1. Abrir Chrome/Edge em `chrome://extensions` ou `edge://extensions`.
2. Ativar modo desenvolvedor.
3. Carregar sem compactacao a pasta `browser_extension/`.
4. Abrir o SEI manualmente com o usuario do servidor.
5. Clicar em `Agente 19`.
