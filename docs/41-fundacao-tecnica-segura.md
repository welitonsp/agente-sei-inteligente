# FASE 40 — Fundação Técnica Segura

## Visão Geral
Esta fase implementa o esqueleto técnico inicial do Agente 19, garantindo que toda a governança e as restrições documentadas sejam transformadas em código impositivo (Guard Rails).

## Principais Componentes Implementados

### 1. Guardião de Ações (SEI Action Guard)
A fonte única da verdade sobre ações vive em `app/core/permissions.py`
(`ALLOWED_ACTIONS`, `FORBIDDEN_ACTIONS`, `SENSITIVE_ACTIONS`), com política de
**negação por padrão**. O guard em `app/sei/sei_action_guard.py` expõe a função
pura `evaluate(GuardRequest) -> GuardResult` e o atalho defensivo
`assert_allowed`, que levanta `PermissionError` quando a ação não é permitida.
A fachada `app/sei/sei_guardian.py` (`SeiGuardian`) encaminha o nome da ação a
esse guard. Atos oficiais (assinar, tramitar, concluir, excluir, dar ciência,
liberar acesso externo, alterar sigilo) são **bloqueio duro**, independentemente
de qualquer flag de ambiente.

### 2. Política de Navegador (Browser Policy)
O `app/sei/browser_policy.py` garante que:
- O painel/robô só aceite a URL base oficial do SEI para login.
- A automação real de browser se inicie por padrão como desabilitada (`ENABLE_SEI_BROWSER_AUTOMATION = False`).
- A criação assistida de minutas requeira explicitamente confirmação humana.

### 3. Auditoria Segura (Audit Safety)
O módulo de auditoria (`app/core/audit.py`) foi desenvolvido com base no princípio de "Privacy by Design":
- O texto integral não é gravado, evitando vazamento de dados sensíveis ou informações sigilosas nos logs de servidor.
- Números de processo são anonimizados com máscara e hash (`process_number_masked`, `process_number_hash`).
- Campos sensíveis submetidos por engano (como `password` ou `cookie` em requests malformadas) são filtrados agressivamente antes de registrar a auditoria.

### 4. Inteligência Institucional Básica e Aprendizado
- O `institutional_analyzer.py` faz classificação de tipo (insensível a acento),
  resumo extractivo real (via `summarizer.py`, sanitizado contra PII) e extração
  estruturada de prazos relativos e absolutos com data-limite (via
  `prazo_extractor.py`). A confiança é derivada de sinais, não fixa.
- O `draft_generator.py` assegura que minutas são produzidas e retidas **apenas em memória** até aprovação humana, sem injeção direta no SEI nesta etapa.
- O `learning_policy.py` implementa a retenção de correções para melhoria de prompts, cuidando explicitamente de não salvar senhas e tokens atrelados à ação.

## Restrições Ativas
- **Não há uso de automação web real** nesta fase. Os limites de segurança foram criados como fundação para a Fase 41.
- A regra-mãe ("o humano assina, tramita e conclui") está totalmente enraizada nas verificações centrais do guardião e testada unitariamente.
