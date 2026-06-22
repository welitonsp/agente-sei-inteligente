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
| Criar estrutura `app/` | NAO_INICIADO |
| Criar `app/core/config.py` | NAO_INICIADO |
| Criar `app/core/permissions.py` | NAO_INICIADO |
| Criar `app/sei/sei_action_guard.py` | NAO_INICIADO |
| Criar `app/core/logger.py` | NAO_INICIADO |
| Criar `app/storage/database.py` | NAO_INICIADO |
| Criar modelos SQLite iniciais | NAO_INICIADO |
| Criar repositorios de auditoria | NAO_INICIADO |
| Criar testes de permissoes | NAO_INICIADO |
| Criar CI basico no GitHub Actions | NAO_INICIADO |

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
| Fundacao tecnica aprovada | BLOQUEADO |
| Politica de dados SEI aprovada | APROVADO |
| Modo sem SEI real aprovado | APROVADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar tela inicial do painel | NAO_INICIADO |
| Campo `Numero do processo SEI` | NAO_INICIADO |
| Campo `Texto copiado do SEI` | NAO_INICIADO |
| Upload de PDF | NAO_INICIADO |
| Botao `Analisar para o 19 CRPM` | NAO_INICIADO |
| Exibir resultado estruturado | NAO_INICIADO |
| Exibir revisao humana obrigatoria | NAO_INICIADO |
| Exibir documentos nao lidos/OCR necessario | NAO_INICIADO |
| Registrar log da analise | NAO_INICIADO |

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
| Painel MVP criado | BLOQUEADO |
| Politica de dados local/efemera implementada | BLOQUEADO |

### Execucao

| Item | Status |
| --- | --- |
| Extrair texto de PDF pesquisavel | NAO_INICIADO |
| Detectar PDF sem texto | NAO_INICIADO |
| Marcar OCR necessario | NAO_INICIADO |
| Gerar hash do documento/texto | NAO_INICIADO |
| Criar inventario de documentos | NAO_INICIADO |
| Marcar documento como lido/parcial/nao_lido | NAO_INICIADO |

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
| Guardiao de seguranca funcionando | BLOQUEADO |
| Logs funcionando | BLOQUEADO |
| Credenciais Google configuradas | BLOQUEADO |
| Grupo de Oficiais definido | BLOQUEADO |

### Execucao

| Item | Status |
| --- | --- |
| Criar servico Google Agenda | NAO_INICIADO |
| Criar evento de teste | NAO_INICIADO |
| Adicionar grupo de Oficiais | NAO_INICIADO |
| Preencher observacao padronizada | NAO_INICIADO |
| Criar chave de duplicidade | NAO_INICIADO |
| Bloquear evento duplicado | NAO_INICIADO |

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
FORA_DO_MVP
```

### Pre-condicoes obrigatorias

| Item | Status |
| --- | --- |
| Autorizacao institucional para extensao | BLOQUEADO |
| Fundacao tecnica aprovada | BLOQUEADO |
| Guardiao testado | BLOQUEADO |
| Politica de dados implementada | BLOQUEADO |
| Painel MVP homologado | BLOQUEADO |
| Testes anti-clique sensivel | BLOQUEADO |

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
| Criar GitHub Actions | NAO_INICIADO |
| Rodar testes unitarios | NAO_INICIADO |
| Rodar testes de permissoes | NAO_INICIADO |
| Bloquear merge se acao proibida for permitida | NAO_INICIADO |
| Rodar lint/format | NAO_INICIADO |
| Checar segredos em arquivos | NAO_INICIADO |

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

## Checklist 12 - FASE 38: Agente SEI RPA Assistido

Objetivo: Permitir que o Agente 19 atue diretamente no SEI apenas para preenchimento, apos acionamento pelo usuario.

### Execucao

| Item | Status |
| --- | --- |
| Implementar acionamento por numero de processo | NAO_INICIADO |
| Garantir que Agente use a sessao sem capturar credenciais | NAO_INICIADO |
| Exportar processo para PDF usando a interface atual | NAO_INICIADO |
| Criar interacao para escolha de minuta (Oficio, Despacho, etc.) | NAO_INICIADO |
| Implementar preenchimento assistido da minuta no SEI | NAO_INICIADO |

### Aceite

1. Senha/token NUNCA e armazenado.
2. Agente so preenche minuta se o humano autorizar.
3. Agente NUNCA assina ou tramita documento.

## Checklist 13 - FASE 39: Memoria Institucional e Aprendizado Supervisionado

Objetivo: Permitir que o Agente 19 aprenda com a unidade.

### Execucao

| Item | Status |
| --- | --- |
| Estruturar banco de dados da Memoria Institucional | NAO_INICIADO |
| Capturar correcoes em minutas antes do envio final | NAO_INICIADO |
| Refinar prompts e sugestoes com base no historico local | NAO_INICIADO |

### Aceite

1. O Agente nao altera regras de negocio de forma autonoma.
2. Dados sensiveis nao vazam para treinar modelos publicos.

## Decisao de inicio

Pode iniciar agora:

```text
Checklist 1 - Fundacao tecnica
Checklist 2 - Painel MVP externo/local, apos fundacao minima
```

Nao iniciar agora:

```text
Checklist 9 - Robozinho real / extensao
```

