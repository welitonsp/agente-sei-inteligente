# Checklist de processos para desenvolvimento

## Objetivo

Definir o processo de desenvolvimento do Agente SEI Inteligente - 19 CRPM com controles claros de entrada, execucao, evidencia, aceite e bloqueio.

Este checklist deve ser usado antes de iniciar cada etapa e antes de considerar qualquer funcionalidade pronta.

## Regra de processo

Nenhuma etapa deve avancar sem:

1. Escopo definido.
2. Risco avaliado.
3. Criterio de aceite escrito.
4. Teste minimo previsto.
5. Evidencia registrada.
6. Bloqueios de seguranca respeitados.

## Status possiveis

```text
NAO_INICIADO
EM_ANDAMENTO
BLOQUEADO
EM_REVISAO
APROVADO
REPROVADO
CONCLUIDO
```

## Checklist 0 - Governanca inicial

| Item | Status | Evidencia |
| --- | --- | --- |
| Repositorio GitHub privado criado | CONCLUIDO | `welitonsp/agente-sei-inteligente` |
| Documentacao base criada | CONCLUIDO | `docs/00` a `docs/26` |
| Matriz de conformidade criada | CONCLUIDO | `docs/26-matriz-conformidade.md` |
| Regra de ouro aprovada | CONCLUIDO | HITL e atos oficiais bloqueados |
| Estrategia sem modulo oficial aprovada | CONCLUIDO | Arquitetura externa/local assistida |
| Dados reais do 19 CRPM preenchidos | BLOQUEADO | Templates ainda com exemplo |
| Definicao de "criar arquivo" | BLOQUEADO | Decisao pendente |

## Checklist 1 - Fundacao tecnica

Objetivo: criar o esqueleto tecnico seguro antes de qualquer IA ou integracao externa.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Repositorio limpo e sincronizado | APROVADO |
| `.env.example` sem segredos reais | APROVADO |
| `.gitignore` protegendo `.env`, banco e caches | APROVADO |
| Decisao SQLite para MVP | APROVADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar estrutura `app/` | CONCLUIDO |
| Criar `app/core/config.py` | CONCLUIDO |
| Criar `app/core/permissions.py` | CONCLUIDO |
| Criar `app/sei/sei_action_guard.py` | CONCLUIDO |
| Criar `app/core/logger.py` | CONCLUIDO (`app/core/logging.py`) |
| Criar `app/storage/database.py` | CONCLUIDO (`app/storage/db.py`) |
| Criar modelos SQLite iniciais | CONCLUIDO (`app/storage/models.py`) |
| Criar repositorios de auditoria | CONCLUIDO (`app/core/audit.py`) |
| Criar testes de permissoes | CONCLUIDO (84 testes totais; TEST-0004) |
| Criar CI basico no GitHub Actions | CONCLUIDO (`.github/workflows/ci.yml`; TEST-0004) |

### Aceite

1. Teste bloqueia todas as acoes proibidas.
2. Teste permite somente acoes declaradas.
3. Banco SQLite inicializa sem erro.
4. Auditoria registra tentativa permitida e bloqueada.
5. Nenhum segredo aparece no repositorio.

### Bloqueios

Nao pode avancar para Agenda, Telegram, IA ou robozinho sem `permissions.py`, `sei_action_guard.py` e testes de bloqueio funcionando.

## Checklist 2 - Painel MVP externo/local

Objetivo: criar uma interface simples para operar sem acessar diretamente o SEI.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Fundacao tecnica aprovada | APROVADO |
| Politica de dados SEI aprovada | APROVADO |
| Modo sem SEI real aprovado | APROVADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar tela inicial do painel | CONCLUIDO (`app/dashboard/local_app.py`; TEST-0006) |
| Campo `Numero do processo SEI` | CONCLUIDO (`ManualTextRequest` + painel local) |
| Campo `Texto copiado do SEI` | CONCLUIDO (`app/intake/manual_text.py` + painel local) |
| Upload de PDF | CONCLUIDO para MVP local (`app/intake/pdf_upload.py`; TEST-0007) |
| Botao `Analisar para o 19 CRPM` | CONCLUIDO no painel local |
| Exibir resultado estruturado | CONCLUIDO no painel local |
| Exibir revisao humana obrigatoria | CONCLUIDO no painel local |
| Exibir documentos nao lidos/OCR necessario | CONCLUIDO para PDF sem texto (`status_leitura=ocr_necessario`) |
| Registrar log da analise | CONCLUIDO no backend de texto manual (TEST-0005) |

### Aceite

1. Funciona sem login no SEI.
2. Nao tenta pesquisar processo no SEI.
3. Nao salva texto integral por padrao.
4. Mostra campos pendentes.
5. Mostra quando revisao humana e obrigatoria.

## Checklist 3 - Leitura de PDF e texto

Objetivo: processar documentos fornecidos pelo servidor.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Painel MVP criado | EM_ANDAMENTO para texto/PDF (autenticacao e views completas pendentes) |
| Politica de dados local/efemera implementada | EM_ANDAMENTO para texto/PDF (sem texto integral; hash/metadados) |

### Execucao

| Item | Status |
| --- | --- |
| Extrair texto de PDF pesquisavel | CONCLUIDO com `pypdf` (TEST-0007) |
| Detectar PDF sem texto | CONCLUIDO (TEST-0007) |
| Marcar OCR necessario | CONCLUIDO como status; OCR real pendente |
| Gerar hash do documento/texto | CONCLUIDO para texto/PDF (TEST-0005, TEST-0007) |
| Criar inventario de documentos | CONCLUIDO para texto/PDF (`Document` com metadados) |
| Marcar documento como lido/parcial/nao_lido | EM_ANDAMENTO (`lido`, `ocr_necessario`, `nao_lido`) |

### Aceite

1. PDF pesquisavel gera texto.
2. PDF sem texto nao gera conclusao falsa.
3. Processo com documento nao lido exige revisao humana.
4. Hash e metadados sao registrados.

## Checklist 4 - Skills administrativas

Objetivo: implementar as primeiras skills sem depender de IA externa sensivel.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Contratos das skills aprovados | APROVADO |
| Dados mestres do 19 CRPM preenchidos | BLOQUEADO |
| Exemplos anonimizados disponiveis | BLOQUEADO |

### Execucao

| Skill | Status |
| --- | --- |
| `sei-leitor-readonly` | NAO_INICIADO |
| `resumidor-administrativo` | NAO_INICIADO |
| `triagem-19crpm` | BLOQUEADO |
| `roteador-unidades-19crpm` | BLOQUEADO |
| `extrator-prazos` | NAO_INICIADO |
| `extrator-eventos` | NAO_INICIADO |
| `minutador-administrativo` | NAO_INICIADO |
| `guardiao-seguranca-sei` | NAO_INICIADO |
| `auditor-processos` | NAO_INICIADO |

### Aceite

1. Toda skill retorna JSON no contrato.
2. Toda skill informa confianca.
3. Toda skill informa fontes usadas.
4. Baixa confianca gera revisao humana.
5. Sem regra real, triagem e roteamento nao inventam unidade.

## Checklist 5 - Knowledge base 19 CRPM

Objetivo: alimentar o agente com regras reais.

### Preenchimento obrigatorio

| Arquivo | Status |
| --- | --- |
| `unidades_19crpm.csv` | BLOQUEADO |
| `unidades_alto_comando.csv` | BLOQUEADO |
| `regras_direcionamento.md` | BLOQUEADO |
| `palavras_chave_19crpm.md` | BLOQUEADO |
| `modelos_resposta.md` | BLOQUEADO |

### Aceite

1. Dados revisados pelo chefe do projeto.
2. Pelo menos 5 casos de teste anonimizados.
3. Pelo menos 3 regras reais de direcionamento.
4. Regra explicita para quando nao houver unidade definida.
5. Roteamento automatico continua bloqueado se regra nao for clara.

## Checklist 6 - Google Agenda

Objetivo: criar agenda e compromissos fora do SEI.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Guardiao de seguranca funcionando | APROVADO |
| Logs funcionando | APROVADO |
| Credenciais Google configuradas | EM_ANDAMENTO (PROC-0004) |
| Grupo de Oficiais definido | APROVADO (marcador OFICIAIS via People API, DEC-0009) |

### Execucao

| Item | Status |
| --- | --- |
| Criar servico Google Agenda | CONCLUIDO (dry-run) |
| Criar evento de teste | CONCLUIDO (simulado; real apos OAuth) |
| Adicionar grupo de Oficiais | CONCLUIDO (resolve e-mails do marcador OFICIAIS) |
| Preencher observacao padronizada | CONCLUIDO |
| Criar chave de duplicidade | CONCLUIDO (local + ICS) |
| Bloquear evento duplicado | CONCLUIDO (status=duplicate) |

### Aceite

1. Evento criado em agenda de teste.
2. Duplicidade bloqueada.
3. Grupo configurado por `.env`.
4. Log registrado.

## Checklist 7 - Telegram / alertas

Objetivo: alertar no celular sem expor documento completo.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Bot Telegram criado | BLOQUEADO |
| Chat/grupo definido | BLOQUEADO |
| Politica de mensagem aprovada | APROVADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar servico Telegram | NAO_INICIADO |
| Enviar alerta informativo | NAO_INICIADO |
| Enviar alerta urgente | NAO_INICIADO |
| Registrar envio | NAO_INICIADO |
| Registrar falha | NAO_INICIADO |

### Aceite

1. Mensagem nao contem documento completo.
2. Falha e registrada.
3. Reenvio nao duplica alerta sem controle.

## Checklist 8 - IA/RAG

Objetivo: usar IA com controle de dados e rastreabilidade.

### Pre-condicoes

| Item | Status |
| --- | --- |
| Politica de dados aprovada | APROVADO |
| Provedor IA definido | BLOQUEADO |
| Conteudo autorizado separado de conteudo real do SEI | BLOQUEADO |

### Execucao

| Item | Status |
| --- | --- |
| Validar modelo configurado na inicializacao | NAO_INICIADO |
| Criar retriever dos manuais | NAO_INICIADO |
| Criar modo local para conteudo vivo | NAO_INICIADO |
| Criar prompts por skill | NAO_INICIADO |
| Criar logs/tracing sanitizados | NAO_INICIADO |
| Criar avaliacao de fidelidade | NAO_INICIADO |

### Aceite

1. Conteudo real do SEI nao vai para IA externa sem autorizacao.
2. Resposta informa fontes.
3. Se nao houver fonte, resposta marca `precisa_revisao`.
4. Prompts nao substituem guardiao de seguranca.

## Checklist 9 - Robozinho real / extensao

Objetivo: criar assistente visual na tela do SEI.

Status atual:

```text
PROTOTIPO_READONLY_EM_ANDAMENTO
```

### Pre-condicoes obrigatorias

| Item | Status |
| --- | --- |
| Autorizacao institucional para extensao | BLOQUEADO para uso real; prototipo local read-only iniciado |
| Fundacao tecnica aprovada | APROVADO |
| Guardiao testado | APROVADO |
| Politica de dados implementada | EM_ANDAMENTO para leitura local/efemera |
| Painel MVP homologado | EM_ANDAMENTO |
| Testes anti-clique sensivel | CONCLUIDO para contrato estatico da extensao (sem `.click()`) |

### Execucao

| Item | Status |
| --- | --- |
| Criar extensao de navegador read-only | CONCLUIDO prototipo (`browser_extension/`) |
| Exibir botao flutuante na tela do SEI | CONCLUIDO (`content.js`, `content.css`) |
| Capturar texto visivel/selecionado | CONCLUIDO prototipo |
| Enviar para backend local | CONCLUIDO (`background.js` -> `127.0.0.1:8000`) |
| Bloquear clique/ato oficial automatico | CONCLUIDO por contrato/teste |
| Homologar em ambiente SEI real | NAO_INICIADO |
| Publicar/instalar de forma institucional | BLOQUEADO |

### Proibido nesta fase

1. Login automatico.
2. Digitar usuario/senha.
3. Guardar cookie/token/sessao.
4. Pesquisar processo por numero.
5. Clicar em botoes do SEI.
6. Escrever no SEI.

## Checklist 10 - CI/CD e qualidade

Objetivo: impedir regressao de seguranca.

### Execucao

| Item | Status |
| --- | --- |
| Criar GitHub Actions | CONCLUIDO (`.github/workflows/ci.yml`) |
| Rodar testes unitarios | CONCLUIDO (84 testes locais; GitHub Actions aprovado no PR #1) |
| Rodar testes de permissoes | CONCLUIDO (gate incluido no `pytest`; GitHub Actions aprovado no PR #1) |
| Bloquear merge se acao proibida for permitida | EM_ANDAMENTO (workflow falha; falta protecao de branch) |
| Rodar lint/format | NAO_INICIADO |
| Checar segredos em arquivos | CONCLUIDO (`scripts/check_no_secrets.py`; GitHub Actions aprovado no PR #1) |

### Aceite

1. PR falha se permissao proibida passar.
2. PR falha se segredo real for detectado.
3. PR falha se contrato JSON obrigatorio quebrar.

## Checklist 11 - Homologacao

Objetivo: validar com exemplos anonimizados antes de usar rotina real.

### Massa minima

| Caso | Status |
| --- | --- |
| E-mail com evento | BLOQUEADO |
| E-mail com prazo | BLOQUEADO |
| PDF pesquisavel | BLOQUEADO |
| PDF sem texto | BLOQUEADO |
| Texto copiado do SEI | BLOQUEADO |
| Processo que nao interessa ao 19 CRPM | BLOQUEADO |
| Processo com unidade indefinida | BLOQUEADO |

### Aceite

1. Nenhuma acao oficial executada.
2. Prazo detectado corretamente.
3. Evento sugerido corretamente.
4. Unidade so sugerida com regra real.
5. Baixa confianca gera revisao humana.
6. Logs permitem auditoria.

## Checklist 12 - Agente 19 Desktop com navegador seguro

Objetivo: permitir uso local sem extensao de navegador, mantendo o login do SEI
exclusivamente na pagina oficial e fora do Agente 19.

Status atual:

```text
PROTOTIPO_IMPLEMENTADO
```

### Pre-condicoes obrigatorias

| Item | Status |
| --- | --- |
| Decisao de nao capturar credenciais do SEI | APROVADO |
| Backend local texto/PDF | APROVADO |
| Guardiao de atos oficiais | APROVADO |
| Extensao institucional indisponivel/bloqueada | IDENTIFICADO |
| Homologacao institucional do desktop | NAO_INICIADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar pacote `app.desktop` | CONCLUIDO |
| Criar comando `.venv\Scripts\python.exe -m app.desktop` | CONCLUIDO |
| Abrir URL oficial do SEI em navegador/janela separada | CONCLUIDO |
| Manter aviso fixo de seguranca | CONCLUIDO |
| Colar texto copiado manualmente do SEI | CONCLUIDO |
| Selecionar PDF exportado manualmente do SEI | CONCLUIDO |
| Analisar texto/PDF via backend local `127.0.0.1` | CONCLUIDO |
| Gerar resumo/tipo provavel/evento/prazo/providencia | CONCLUIDO no prototipo |
| Copiar resultado | CONCLUIDO |
| Bloquear campos/payloads com credenciais | CONCLUIDO |
| Testar ausencia de campo senha/login SEI | CONCLUIDO |
| Homologar desktop em ambiente institucional | NAO_INICIADO |

### Proibido nesta fase

1. Pedir usuario ou senha do SEI.
2. Salvar usuario ou senha do SEI.
3. Ler cookie, sessao, token ou localStorage/sessionStorage.
4. Automatizar clique no SEI.
5. Assinar, tramitar, enviar, concluir ou criar documento oficial no SEI.
6. Inserir conteudo no SEI sem acao humana.
7. Burlar politica institucional de extensao ou navegador.

## Decisao de continuidade

Pode continuar agora:

```text
Checklist 2 - Painel MVP externo/local
Checklist 3 - Leitura de PDF e texto
Checklist 6 - Google Agenda, conclusao do OAuth
Checklist 9 - Robozinho/extensao SEI read-only, somente prototipo e homologacao
Checklist 12 - Agente 19 Desktop com navegador seguro, somente prototipo e homologacao
```

Nao iniciar agora sem nova autorizacao:

```text
Clique automatico no SEI
Login automatico no SEI
Uso institucional da extensao sem homologacao
IA externa com conteudo real do SEI
Triagem automatica sem knowledge base real
```
