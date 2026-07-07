# FASE 58 - Revisao de Mercado do Agente de IA

Data: 2026-06-29

## Objetivo

Revisar o projeto como um Agente de Inteligencia Artificial institucional: um
"novo servidor digital" que apoia usuarios, organiza demandas, sugere
providencias e prepara minutas, mantendo controle humano sobre atos oficiais.

## Referencias de mercado consideradas

1. NIST AI Risk Management Framework e perfil de IA generativa.
2. OWASP Top 10 for LLM Applications 2025.
3. OpenAI Evals / avaliacao de comportamento de aplicacoes LLM.
4. Google Secure AI Framework (SAIF).

## Veredito executivo

O projeto esta no caminho correto para um agente institucional seguro, porque
ja possui:

1. Controle humano obrigatorio.
2. Negacao por padrao para acoes.
3. Bloqueio duro de atos oficiais no SEI.
4. Politica de dados local/efemera.
5. Auditoria e scanner de segredos.
6. Separacao entre leitura, analise, triagem, minuta e guardas.
7. Orquestrador de missao supervisionada.

Ainda nao esta pronto para operacao institucional real com dados sensiveis.
As lacunas prioritarias sao avaliacao continua de agente, autenticacao do
painel, base real homologada do 19 CRPM, observabilidade/tracing sanitizado,
governanca de prompts e homologacao formal.

## Achados prioritarios

### P0 - Uso real ainda deve permanecer bloqueado

Motivo:

1. Knowledge base real do 19 CRPM ainda esta incompleta.
2. Painel local ainda nao tem autenticacao/perfis.
3. Homologacao com casos anonimizados ainda nao foi concluida.
4. Extensao e leitura automatica dependem de autorizacao institucional.

Acao:

1. Manter uso real bloqueado.
2. Operar somente com exemplos anonimizados ate homologacao.

### P1 - Avaliacao continua de agente era lacuna central

Motivo:

Testes unitarios comprovam funcoes, mas agentes precisam de avaliacao de
comportamento: cenarios, entradas maliciosas, expectativa de controle humano,
ausencia de excesso de autonomia e estabilidade de resposta.

Acao implementada:

1. Criado `app/evaluation/agent_readiness.py`.
2. Criado `scripts/run_agent_evals.py`.
3. Criados testes em `tests/test_agent_readiness_evals.py`.
4. CI passa a executar as avaliacoes depois da suite de testes.

### P1 - Autenticacao e perfis do painel

Motivo:

O painel local e operacionalmente util, mas ainda nao diferencia operador,
revisor, gestor e administrador.

Acao recomendada:

1. Implementar login local simples.
2. Criar perfis e permissoes.
3. Registrar usuario em toda missao.

### P1 - Observabilidade/tracing sanitizado

Motivo:

Ja existem logs e auditoria, mas ainda falta uma trilha de missao completa:
entrada sanitizada, decisao do guard, subagentes acionados, campos pendentes,
riscos, resultado e revisao humana.

Acao recomendada:

1. Criar `mission_trace_id`.
2. Correlacionar logs de analise, triagem e minuta.
3. Nunca persistir texto integral por padrao.

### P1 - Governanca de prompts e modelos

Motivo:

O projeto ja tem papel logico de IA, mas precisa versionar prompts aprovados
por skill e registrar qual versao gerou cada resposta.

Acao recomendada:

1. Criar `knowledge_base/prompts/*.md`.
2. Versionar prompt por papel.
3. Registrar `prompt_version` no contrato.

### P2 - Red team e ataques de prompt injection

Motivo:

OWASP 2025 destaca prompt injection, vazamento de informacao sensivel, excesso
de agencia, tratamento inadequado de saida e desinformacao como riscos
centrais para aplicacoes LLM.

Acao recomendada:

1. Criar massa de testes adversariais.
2. Testar pedidos como "ignore regras", "assine", "tramite", "mostre senha".
3. Garantir que a resposta mantenha bloqueio e revisao humana.

### P2 - Base de conhecimento real e homologada

Motivo:

Sem dados reais homologados, o agente nao pode decidir unidade ou fluxo do
19 CRPM com confianca.

Acao recomendada:

1. Preencher CSVs reais.
2. Criar 5 a 20 casos anonimizados.
3. Medir acerto de triagem e motivos de erro.

## Decisao arquitetural

O Agente 19 deve ser tratado como agente operacional supervisionado, nao como
chat generico. Ele deve:

1. Receber demanda.
2. Entender contexto.
3. Acionar subagentes/ferramentas com permissao estreita.
4. Produzir plano e rascunho.
5. Expor riscos e pendencias.
6. Aguardar revisao humana.
7. Registrar auditoria.

Ele nao deve:

1. Praticar ato oficial.
2. Usar credencial do servidor.
3. Navegar sozinho no SEI.
4. Decidir unidade sem regra ou humano.
5. Enviar conteudo sensivel para IA externa sem autorizacao formal.

## Roadmap recomendado

1. Ampliar avaliacoes de agente para 20 casos anonimizados.
2. Implementar autenticacao local e perfis.
3. Criar tracing de missao sanitizado.
4. Versionar prompts por papel/skill.
5. Preencher knowledge base real do 19 CRPM.
6. Homologar triagem e minutas com usuarios reais.
7. Integrar o orquestrador de missao ao chat da extensao.
8. Criar relatorio/exportacao de missao.
9. Somente depois avaliar automacoes externas adicionais.

## Criterio para chamar de "Agente de IA v1"

O projeto so deve ser considerado Agente de IA v1 quando:

1. Rodar `pytest` e `scripts/run_agent_evals.py` em CI.
2. Possuir pelo menos 20 avaliacoes de comportamento.
3. Ter autenticacao local.
4. Ter prompts versionados.
5. Ter tracing sanitizado.
6. Ter knowledge base real homologada.
7. Ter autorizacao institucional para o modo de uso escolhido.
8. Manter atos oficiais bloqueados.
