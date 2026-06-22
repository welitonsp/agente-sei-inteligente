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
