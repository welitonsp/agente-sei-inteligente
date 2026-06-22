# Matriz de conformidade do projeto

Data da avaliacao: 2026-06-22

## Objetivo

Registrar o que esta em conformidade, parcialmente conforme e nao conforme no projeto Agente SEI Inteligente - 19 CRPM.

Esta matriz avalia a conformidade do projeto com a propria arquitetura definida na documentacao. Nao substitui parecer juridico, parecer de seguranca institucional ou autorizacao formal do orgao gestor do SEI.

## Legenda

| Status | Significado |
| --- | --- |
| Conforme | Atende ao desenho e pode seguir para a proxima etapa |
| Parcialmente conforme | Conceito correto, mas falta decisao, dado real, teste ou implementacao |
| Nao conforme | Bloqueia uso real ou desenvolvimento daquela parte ate correcao |
| Fora do MVP | Nao deve ser implementado agora |

## Veredito executivo

O projeto esta:

```text
Conforme para iniciar desenvolvimento da fundacao tecnica.
Nao conforme para operacao real.
Nao conforme para automacao direta no SEI.
Nao conforme para uso de conteudo real do SEI em IA externa.
```

Desenvolvimento autorizado como proximo passo:

```text
Etapa 2 - Fundacao tecnica
```

Com escopo limitado a:

1. Estrutura `app/`.
2. Permissoes.
3. Guardiao de seguranca.
4. SQLite.
5. Logs.
6. Testes de bloqueio.
7. Painel MVP com texto colado/PDF.

## Itens em conformidade

| ID | Item | Status | Evidencia | Decisao |
| --- | --- | --- | --- | --- |
| C-01 | Regra de ouro HITL | Conforme | Agente prepara, humano decide | Manter |
| C-02 | Bloqueio de atos oficiais | Conforme | Assinar, enviar, tramitar, concluir, ciencia, excluir e cancelar proibidos | Manter como regra permanente |
| C-03 | Identidade individual do servidor | Conforme | Sem usuario unico; servidor usa propria sessao | Manter |
| C-04 | Proibicao de guardar senha/cookie/token | Conforme | Politica de identidade e dados | Manter |
| C-05 | Estrategia sem modulo oficial SEI IA | Conforme | Arquitetura externa/local assistida | Manter |
| C-06 | Robozinho fora do codigo do SEI | Conforme | Extensao/painel local read-only, nao modulo interno | Manter |
| C-07 | MVP sem navegacao automatica no SEI | Conforme | Numero do processo e apenas identificacao/conferencia | Manter |
| C-08 | Politica de dados local/efemera | Conforme | `SEI_DATA_MODE=local_only`, `SEI_TEXT_RETENTION=ephemeral` | Manter |
| C-09 | Conteudo real do SEI fora de IA externa | Conforme | `SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT=false` | Manter |
| C-10 | Separacao por skills especialistas | Conforme | Skills e contratos documentados | Usar no codigo |
| C-11 | WebServices de escrita bloqueados | Conforme | Escrita bloqueada ate autorizacao formal | Manter |
| C-12 | Repositorio GitHub privado | Conforme | Repositorio `welitonsp/agente-sei-inteligente` privado | Manter |

## Itens parcialmente conformes

| ID | Item | Status | Lacuna | Acao necessaria |
| --- | --- | --- | --- | --- |
| P-01 | Fundacao tecnica | Conforme | Implementada, testada (84 testes; TEST-0004), PR #1 aberto e GitHub Actions aprovado | Configurar protecao da branch `main` antes do merge |
| P-02 | Banco de dados | Conforme | SQLite com 8 entidades em `app/storage/models.py`; `scripts/init_db.py` | Migrar para PostgreSQL apenas se necessario |
| P-03 | Skills especialistas | Parcialmente conforme | Contratos existem; codigo nao existe | Implementar classes/funcoes e testes por skill |
| P-04 | Knowledge base do 19 CRPM | Parcialmente conforme | Arquivos sao templates com exemplos | Preencher unidades, Alto Comando, palavras-chave e regras reais |
| P-05 | Prompts aprovados | Parcialmente conforme | Apenas prompt base existe | Criar prompts por skill |
| P-06 | Google Agenda | Parcialmente conforme | Servico implementado e testado em dry-run; falta concluir OAuth real | Concluir credenciais OAuth (PROC-0004) e homologar evento real |
| P-07 | Telegram | Parcialmente conforme | Padrao documentado; bot/token/codigo ausentes | Implementar envio isolado e teste |
| P-08 | PDF | Parcialmente conforme | Estrategia documentada; extrator nao implementado | Implementar upload, extracao e tratamento OCR necessario |
| P-09 | IA/RAG | Parcialmente conforme | Provedor padrao decidido: Claude (DEC-0006); retriever ainda nao implementado | Implementar cliente Claude e retriever na Etapa 7 |
| P-10 | Modelos Gemini | Parcialmente conforme | IDs do `.env.example` sao invalidos; provedor padrao agora e Claude | Corrigir/remover IDs Gemini se houver uso futuro |
| P-11 | Observabilidade de LLM | Parcialmente conforme | Logs existem no desenho; tracing de prompts nao definido | Definir se sera Phoenix, LangSmith ou log local sanitizado |
| P-12 | Avaliacao automatizada de IA | Parcialmente conforme | Plano de testes existe; RAGAS/TruLens ou avaliador proprio nao definido | Adicionar avaliacao de fidelidade e ausencia de invencao |
| P-13 | Autenticacao do painel | Parcialmente conforme | Necessidade documentada; mecanismo nao escolhido | Definir login local, usuarios e perfis |
| P-14 | Retencao de logs | Parcialmente conforme | Politica geral existe; prazo institucional falta | Definir prazo e responsavel por auditoria |

## Nao conformidades atuais

| ID | Item | Status | Motivo | Correcao |
| --- | --- | --- | --- | --- |
| NC-01 | Operacao real do agente | Nao conforme | Nao existe codigo de aplicacao | Implementar MVP e homologar |
| NC-02 | Gate automatico de seguranca | Parcialmente conforme | Workflow CI criado e aprovado no PR #1; protecao de branch ainda pendente | Configurar protecao da `main` |
| NC-03 | Triagem automatica 19 CRPM | Nao conforme | Dados mestres reais ausentes | Preencher `knowledge_base/fluxos_19crpm/` |
| NC-04 | Direcionamento para unidade responsavel | Nao conforme | Sem regras reais, o agente poderia inventar | Bloquear decisao automatica ate regras reais |
| NC-05 | Definicao de "criar arquivo" | Nao conforme | Termo ainda ambiguo | Definir se e minuta `.docx`, PDF, texto, pasta ou registro |
| NC-06 | Extensao real do robozinho | Parcialmente conforme | Prototipo read-only criado; falta autorizacao/homologacao institucional | Manter read-only, sem clique automatico, ate autorizacao formal |
| NC-07 | Leitura automatica do SEI por numero | Nao conforme | Risco de navegacao automatica e clique indevido | Manter proibida no MVP |
| NC-08 | Uso de conteudo real do SEI em IA externa | Nao conforme | Sem autorizacao formal | Manter bloqueado |
| NC-09 | Escrita no SEI via WebServices | Nao conforme | Contraria estrategia de sessao individual e exige autorizacao formal | Manter bloqueada |

## Fora do MVP

| Item | Motivo |
| --- | --- |
| Extensao de navegador real | Prototipo read-only iniciado; uso real exige autorizacao e homologacao |
| Playwright conectado ao SEI | Risco de clique/navegacao indevida |
| Busca automatica por numero de processo no SEI | Pode virar automacao de navegacao |
| Escrita de minuta dentro do SEI | Sem modulo oficial e sem autorizacao |
| WebServices de escrita | Nao preserva naturalmente a sessao individual |
| Envio de documento real do SEI para Gemini | Bloqueado por politica de dados |

## Conformidade para desenvolvimento por fase

| Fase | Status | Condicao |
| --- | --- | --- |
| Etapa 1 - Documentacao | Conforme | Concluida |
| Etapa 2 - Fundacao tecnica | Conforme | Implementada, testada (84 testes), PR #1 aberto e CI aprovado |
| Etapa 3 - Google Agenda | Em andamento | Servico pronto em dry-run; falta OAuth real |
| Etapa 4 - Telegram | Condicionada | Apos logs e politica de mensagem |
| Etapa 5 - E-mail | Condicionada | Apos decisao do provedor e credenciais |
| Etapa 6 - PDF | Em andamento | Upload e extração de PDF pesquisável prontos; OCR real pendente |
| Etapa 7 - Inteligencia administrativa | Condicionada | Apos dados reais ou exemplos anonimizados |
| Etapa 8 - Interface web | Em andamento | Painel local de texto/PDF pronto; falta autenticação e views completas |
| Etapa 9 - SEI read-only | Em prototipo | Extensao read-only criada; uso real depende de autorizacao/homologacao |
| Etapa 10 - Minutador SEI assistido | Nao liberada | Minutas apenas fora do SEI por enquanto |
| Etapa 11 - Operacao v1 | Nao liberada | Depende de homologacao completa |

## Ordem obrigatoria de correcao

1. Implementar fundacao tecnica.
2. Criar testes de permissoes e bloqueios.
3. Criar SQLite e auditoria.
4. Criar painel MVP sem SEI real.
5. Preencher dados mestres do 19 CRPM.
6. Implementar triagem com revisao humana obrigatoria.
7. Integrar Agenda e Telegram isoladamente.
8. Avaliar IA/RAG com dados nao sensiveis.
9. Homologar com exemplos anonimizados.
10. So depois discutir robozinho read-only real.

## Decisao do chefe do projeto

Fica aprovado iniciar desenvolvimento apenas da fundacao tecnica e do MVP externo/local.

Fica proibido, nesta fase:

1. Automatizar login no SEI.
2. Navegar no SEI por numero de processo.
3. Clicar em qualquer botao do SEI.
4. Escrever no SEI.
5. Enviar conteudo real do SEI para IA externa.
6. Decidir unidade do 19 CRPM sem regras reais.
