# Registro de testes e homologacao

Este documento registra testes manuais, homologacoes e evidencias.

Nao registrar dados reais sensiveis. Usar exemplos anonimizados.

## Formato

```text
ID:
Data:
Versao/commit:
Ambiente:
Responsavel:
Caso testado:
Entrada usada:
Resultado esperado:
Resultado obtido:
Evidencia:
Status:
Problemas encontrados:
Proximo passo:
```

## TEST-0001

Data:  
Versao/commit:  
Ambiente:  
Responsavel:  
Caso testado:  
Entrada usada:  
Resultado esperado:  
Resultado obtido:  
Evidencia:  
Status: NAO_INICIADO  
Problemas encontrados:  
Proximo passo:

## TEST-0002

Data: 2026-06-21  
Versao/commit: branch `feat/fundacao-agenda-ics` (commit 1f40708 + docs)  
Ambiente: Local Windows, Python 3.13, `.venv`, pytest  
Responsavel: Engenharia do projeto (com Claude Code)  
Caso testado: Suite automatizada da fundacao tecnica, agenda, contatos, ICS e OAuth.  
Entrada usada: Dados ficticios/anonimos; backends em memoria; ICS via fixture.  
Resultado esperado: Acoes proibidas bloqueadas; segredos nao persistidos; dedup e guard corretos.  
Resultado obtido: 81 testes passando.  
Evidencia: `pytest` verde (saida do terminal); arquivos em `tests/`.  
Status: APROVADO  
Problemas encontrados: Nenhum bloqueante. CI no GitHub Actions ainda pendente.  
Proximo passo: Adicionar workflow de CI e validar OAuth real.

## TEST-0003

Data: 2026-06-21  
Versao/commit: branch `feat/fundacao-agenda-ics`  
Ambiente: Local Windows, `.venv`  
Responsavel: Engenharia do projeto  
Caso testado: Leitura do feed iCal real (somente leitura, sem expor titulos).  
Entrada usada: `GOOGLE_CALENDAR_ICS_URL` do `.env` (agenda 19crpm.pm).  
Resultado esperado: Parser le e estrutura os eventos sem erro.  
Resultado obtido: 985 eventos parseados (873 com horario, 112 dia inteiro), intervalo 2022-2026.  
Evidencia: Execucao de `ics_reader.read_calendar` reportando apenas agregados.  
Status: APROVADO  
Problemas encontrados: Nenhum. Nenhum titulo/dado sensivel foi registrado.  
Proximo passo: Usar o dedup ICS antes de criar evento real apos OAuth.

## TEST-0004

Data: 2026-06-22  
Versao/commit: branch `feat/fundacao-agenda-ics`  
Ambiente: Local Windows, Python 3.13, `.venv`, pytest  
Responsavel: Engenharia do projeto  
Caso testado: Gate CI local: sintaxe do scanner de segredos, varredura dos arquivos versionados e suite automatizada completa.  
Entrada usada: Arquivos conhecidos pelo Git e novos nao ignorados; dados ficticios/anonimos nos testes.  
Resultado esperado: Nenhum segredo concreto detectado; todos os testes passam.  
Resultado obtido: `scripts/check_no_secrets.py` OK; 84 testes passando localmente; GitHub Actions aprovado no PR #1 em Python 3.11 e 3.13.  
Evidencia: Execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`; checks do PR #1.  
Status: APROVADO  
Problemas encontrados: Scanner inicialmente gerou falso positivo em atributos de teste (`google_client_secret`/`google_refresh_token`) e o teste de import precisava registrar o modulo em `sys.modules`; ambos corrigidos.  
Proximo passo: Configurar protecao da branch `main` e concluir o OAuth real.

## TEST-0005

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Intake manual de texto (`IMPORT_TEXT`) para o MVP externo/local.
Entrada usada: Textos ficticios/anonimos com evento, prazo e marcador sensivel de teste.
Resultado esperado: Nao acessar SEI real; nao persistir texto integral; registrar hash/metadados; exigir revisao humana; detectar evento/prazo simples.
Resultado obtido: `scripts/check_no_secrets.py` OK; 89 testes passando; texto integral e marcador sensivel nao apareceram em documento nem auditoria.
Evidencia: `tests/test_manual_text_intake.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Criar API/tela MVP para acionar `manual_text.analyze_text` e exibir resultado estruturado.

## TEST-0006

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Painel MVP local para texto colado.
Entrada usada: HTML do painel e textos ficticios/anonimos enviados ao endpoint local `IMPORT_TEXT`.
Resultado esperado: Tela contem campos minimos do checklist; endpoint retorna resultado estruturado; texto integral nao volta na resposta.
Resultado obtido: `scripts/check_no_secrets.py` OK; 92 testes passando.
Evidencia: `tests/test_dashboard_local_app.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Rodar painel localmente, validar usabilidade visual e iniciar upload PDF/OCR ou autenticacao local.

## TEST-0007

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Upload local de PDF pesquisável, PDF sem texto extraível e PDF inválido.
Entrada usada: PDFs fictícios/anonimizados gerados em teste, com e sem texto extraível.
Resultado esperado: PDF pesquisável gera hash/metadados/resumo; PDF sem texto marca `ocr_necessario`; PDF inválido não cria documento; texto integral não é persistido nem auditado.
Resultado obtido: `scripts/check_no_secrets.py` OK; 97 testes passando.
Evidencia: `tests/test_pdf_upload_intake.py`, execução local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Validar upload PDF no painel local e decidir entre OCR real ou autenticação local do painel.

## TEST-0008

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Contrato estatico de seguranca da extensao SEI read-only.
Entrada usada: Arquivos `browser_extension/manifest.json`, `content.js` e `background.js`.
Resultado esperado: Extensao restrita ao SEI/localhost, sem permissao de cookies/webRequest, sem clique automatico e com bloqueio de termos de atos oficiais.
Resultado obtido: Testes de contrato da extensao aprovados; scanner sem segredos.
Evidencia: `tests/test_browser_extension_contract.py`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Homologar manualmente a extensao na tela real do SEI com backend local ativo.

## TEST-0009

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Contrato de seguranca do Agente 19 Desktop com navegador seguro.
Entrada usada: Arquivos `app/desktop/secure_browser.py` e testes automatizados.
Resultado esperado: Desktop abre somente URL oficial do SEI, comunica apenas com `127.0.0.1`, nao possui campo de senha/login SEI, nao persiste credenciais e nao executa clique/ato oficial.
Resultado obtido: `scripts/check_no_secrets.py` OK; 107 testes passando.
Evidencia: `tests/test_desktop_secure_browser.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Homologar manualmente o desktop em ambiente institucional com exemplos anonimizados.

## TEST-0010

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Minutador local zero custo por regras e templates.
Entrada usada: Textos e metadados ficticios/anonimizados para despacho, oficio, informacao e encaminhamento.
Resultado esperado: Gerar rascunho local com revisao humana obrigatoria, acoes oficiais bloqueadas, campos pendentes quando faltar dado e auditoria sem texto integral.
Resultado obtido: `scripts/check_no_secrets.py` OK; 117 testes passando.
Evidencia: `tests/test_local_minutador.py`, painel local e desktop usando `POST /api/generate-draft`; execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Homologar minutas com exemplos anonimizados do 19 CRPM.

## TEST-0011

Data: 2026-06-22
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Knowledge base local e triagem/roteamento por regras.
Entrada usada: CSVs vazios versionados e fixtures temporarias com regras ficticias.
Resultado esperado: Sem regras, nao inventar unidade; com regra valida ficticia, sugerir unidade/tipo/providencia; se a unidade da regra nao estiver cadastrada, nao sugerir unidade.
Resultado obtido: `scripts/check_no_secrets.py` OK; 123 testes passando.
Evidencia: `tests/test_local_knowledge_base.py`, endpoint `POST /api/triage-local`; execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Preencher knowledge base real e homologar com casos anonimizados.

## TEST-0012

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: PATCH 4 de hardening da FASE 5A - minuta controlada simulada.
Entrada usada: Configuracoes `APP_ENV=prod/local`, tokens de minuta, textos ficticios, processos ficticios e varredura estatica de `app/`.
Resultado esperado: Bloquear `MINUTA_TOKEN_SECRET` padrao/curto em producao; bloquear `ENABLE_MINUTA_CREATION=true` em producao; falhar token se texto mudar; auditar `text_hash` sem texto integral; manter escrita real como `NotImplementedError`; impedir uso direto de Playwright fora de `app/sei/playwright_session.py`.
Resultado obtido: `scripts/check_no_secrets.py` OK; 131 testes passando.
Evidencia: `tests/test_phase5a_minuta_controlada.py`, `app/core/safety.py`, `app/sei/minuta_writer.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Preparar FASE 5B apenas em homologacao, com seletores reais validados e nivel de acesso explicito.

## TEST-0013

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: FASE 5B-homologacao - cadastro de minuta, nivel de acesso e manifesto de seletores.
Entrada usada: Cadastros ficticios, manifesto de seletores ficticio homologado e manifesto template incompleto.
Resultado esperado: `nivel_acesso` obrigatorio; restrito/sigiloso exige `hipotese_legal`; campos aplicaveis sao validados; manifesto exige seletores homologados; seletores de atos oficiais sao bloqueados; `real_write_allowed=false`.
Resultado obtido: `scripts/check_no_secrets.py` OK; 138 testes passando.
Evidencia: `tests/test_phase5b_homologacao.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Rodar suite completa e preencher manifesto apenas em homologacao controlada.

## TEST-0014

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Diagnostico seguro de API SEI/WSSEI.
Entrada usada: URL oficial ficticia do SEI, opener fake e erros HTTP simulados.
Resultado esperado: Montar candidatos `mod-wssei-v2`, `mod-wssei-v1` e WSDL; recusar URL com credencial; nao enviar Cookie/Authorization/payload; classificar status HTTP sem autorizar uso real.
Resultado obtido: `scripts/check_no_secrets.py` OK; 144 testes passando.
Evidencia: `tests/test_sei_api_discovery.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Rodar diagnostico real manualmente com `scripts/sei_api_discovery.py` e registrar resultado.

## TEST-0015

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`
Responsavel: Engenharia do projeto
Caso testado: Execucao real do diagnostico seguro de API SEI/WSSEI contra `https://sei.go.gov.br/sei/`.
Entrada usada: URLs candidatas geradas automaticamente, sem credenciais.
Resultado esperado: Consultar candidatos sem usuario, senha, cookie, token, sessao ou payload; classificar resultado sem autorizar uso real.
Resultado obtido: `mod-wssei-v2` retornou 404; `mod-wssei-v1` retornou 404; `sei-soap-wsdl` ficou indisponivel com conexao encerrada pelo host remoto.
Evidencia: Execucao local de `.venv\Scripts\python.exe scripts\sei_api_discovery.py`; documento `docs/42-resultado-diagnostico-real-api-sei.md`.
Status: APROVADO
Problemas encontrados: Script inicialmente precisava ajustar `sys.path`; diagnostico tambem precisou tratar conexao encerrada pelo host remoto. Ambos corrigidos.
Validacao final: `scripts/check_no_secrets.py` OK; 145 testes passando.
Proximo passo: Manter API real bloqueada ate haver endpoint autorizado/informacao oficial.

## TEST-0016

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Contrato da UI chat do Agente 19 na extensao SEI read-only.
Entrada usada: `browser_extension/content.js`, `content.css`, `manifest.json` e testes automatizados.
Resultado esperado: Extensao possui UI de chat lateral, acoes rapidas, campo de pergunta, aviso de seguranca e continua sem cookies, senha, sessao, storage ou clique automatico.
Resultado obtido: `scripts/check_no_secrets.py` OK; 147 testes passando.
Evidencia: `tests/test_browser_extension_contract.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Homologar visualmente no SEI com backend local e conteudo anonimizado/nao sensivel.

## TEST-0017

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: Preview local da UI chat do Agente 19.
Entrada usada: `browser_extension/preview_chat.html`.
Resultado esperado: Preview carrega CSS/JS da extensao, usa dados ficticios, possui resposta simulada e nao contem senha, cookie, token, storage ou endpoint real.
Resultado obtido: `scripts/check_no_secrets.py` OK; 149 testes passando.
Evidencia: `tests/test_browser_extension_contract.py`, execucao local de `python scripts/check_no_secrets.py .` e `python -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Abrir `browser_extension/preview_chat.html` no navegador e registrar feedback visual.

## TEST-0018

Data: 2026-06-23
Versao/commit: branch `feat/fundacao-agenda-ics`
Ambiente: Local Windows, Python 3.13, `.venv`, pytest
Responsavel: Engenharia do projeto
Caso testado: UX Chat V2 e minuta externa supervisionada.
Entrada usada: `browser_extension/content.js`, `content.css`, `preview_chat.html` e `manifest.json`.
Resultado esperado: Chat exibe status operacional, oferece acao `Minuta` apenas como rascunho externo, informa revisao humana e continua sem clique automatico, storage, cookie, senha ou sessao.
Resultado obtido: `scripts/check_no_secrets.py` OK; 150 testes passando.
Evidencia: `tests/test_browser_extension_contract.py`, execucao local de `.venv\Scripts\python.exe scripts\check_no_secrets.py .` e `.venv\Scripts\python.exe -m pytest`.
Status: APROVADO
Problemas encontrados: Nenhum bloqueante.
Proximo passo: Homologar visualmente a UI V2 no preview local com o usuario.
