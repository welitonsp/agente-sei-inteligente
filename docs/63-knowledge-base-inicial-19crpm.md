# Fase 63 - Knowledge base inicial do Agente 19

Data: 2026-06-29

## Objetivo

Dar ao Agente 19 uma memoria operacional inicial, local e auditavel para
triagem do interesse do 19 CRPM, sem depender de IA externa e sem executar atos
oficiais no SEI.

## O que mudou

1. `knowledge_base/fluxos_19crpm/unidades_19crpm.csv` recebeu a unidade
   `PM/19 CRPM`.
2. `knowledge_base/fluxos_19crpm/palavras_chave_19crpm.csv` recebeu termos
   conservadores para mencao direta e apoio operacional.
3. `knowledge_base/fluxos_19crpm/regras_direcionamento.csv` recebeu regras
   iniciais para:
   - mencao direta ao 19 CRPM;
   - apoio operacional/evento/policiamento;
   - demandas administrativas de conhecimento e providencias.
4. `app/intelligence/local_triage.py` passou a normalizar acentos, ordinal
   `19º` e pontuacao antes de aplicar regras.
5. A triagem agora devolve `evidencias` com os termos que ativaram a regra.
6. A resposta do Agente 19 passou a exibir unidade sugerida, regra aplicada e
   evidencias.

## Garantias

1. Toda triagem continua com revisao humana obrigatoria.
2. Regra sem unidade cadastrada nao sugere unidade.
3. Texto sem regra continua pendente e nao inventa destino.
4. Acoes oficiais continuam bloqueadas:
   - assinar documento;
   - enviar processo;
   - tramitar processo;
   - concluir processo;
   - dar ciencia automatica;
   - excluir ou cancelar documento;
   - alterar sigilo/acesso.

## Limites

Esta fase nao substitui homologacao com exemplos reais anonimizados. As regras
iniciais sao um ponto de partida seguro para testes assistidos pelo operador.

## Proximo passo

Registrar correcoes feitas pelo operador e transformar essas correcoes em novas
regras versionadas, mantendo sempre revisao humana obrigatoria.
