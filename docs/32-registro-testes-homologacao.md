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

