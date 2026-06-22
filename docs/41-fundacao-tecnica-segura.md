# FASE 40 — Fundação Técnica Segura

## Visão Geral
Esta fase implementa o esqueleto técnico inicial do Agente 19, garantindo que toda a governança e as restrições documentadas sejam transformadas em código impositivo (Guard Rails).

## Principais Componentes Implementados

### 1. Guardião de Ações (SEI Action Guard)
O arquivo `app/sei/sei_action_guard.py` contém uma lista rígida de ações proibidas (`PROHIBITED_ACTIONS`). A função `validate_action` atua como interceptadora, lançando `ActionBlockedError` caso haja qualquer tentativa de:
- Assinar, tramitar, concluir ou excluir documentos/processos.
- Capturar ou vazar senhas, cookies, sessões ou tokens.

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
- O `institutional_analyzer.py` introduz classificações básicas (ex. identificação de ofícios e prazos).
- O `draft_generator.py` assegura que minutas são produzidas e retidas **apenas em memória** até aprovação humana, sem injeção direta no SEI nesta etapa.
- O `learning_policy.py` implementa a retenção de correções para melhoria de prompts, cuidando explicitamente de não salvar senhas e tokens atrelados à ação.

## Restrições Ativas
- **Não há uso de automação web real** nesta fase. Os limites de segurança foram criados como fundação para a Fase 41.
- A regra-mãe ("o humano assina, tramita e conclui") está totalmente enraizada nas verificações centrais do guardião e testada unitariamente.
