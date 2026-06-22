# FASE 41 — Banco SQLite e Memória Institucional Inicial

## Visão Geral
Como Funcionário Digital de IA, o Agente 19 precisa armazenar aprendizados, regras de roteamento e históricos de decisões sem ferir os rígidos princípios de segurança institucional. 
Para tal, implementamos a **Memória Institucional** com SQLite: uma solução embutida e local que mantém os dados seguros na própria máquina host.

## Tabelas Iniciais e Seus Papéis

- `unidades_pmgo`: Cadastro interno de unidades que o 19º CRPM atende ou gerencia, com suas siglas, tipos e e-mails. É a base para roteamento de documentos.
- `modelos_aprovados`: Repositório de minutas padronizadas ("o jeito do quartel"). Textos boilerplate ou esqueletos de Ofícios.
- `correcoes_usuario`: O aprendizado supervisionado. Em vez de gravar texto bruto para retreinar IAs externas (o que é proibido), o sistema grava *hashes* e *resumos* para entender "onde" os modelos devem ser melhorados no prompt, ou qual tipo de correção é frequentemente exigida.
- `decisoes_validadas`: Registra a aceitação de uma sugestão de IA. Se a IA sugere "Responder ao BPTUR" e o servidor aprova, isso entra como precedente válido.
- `regras_aprendizado`: Regras manuais adicionadas pelos administradores do sistema em cima do aprendizado (ex: 'Se for documento de X, envie para Y').
- `auditoria_eventos`: Gravação imutável de eventos passados pelo guardião de ações (`app/core/audit.py`). 

## Política de Dados
Seguindo o `app/sei/browser_policy.py`, a base SQLite:
- **Não** armazena textos integrais de processos ativos (`full_text`).
- **Não** armazena nenhum tipo de credencial (senha, cookie, sessão).
- Todas as listagens sensíveis anonimizam ou usam `hash` em `process_number_hash` e `texto_original_hash`.

## Comandos de Inicialização e Seed
Para preparar a base para produção/homologação sem afetar código:
```powershell
python scripts/init_db.py
python scripts/seed_19crpm.py
```
O banco será salvo no diretório `/data` na raiz do projeto (que já está inserido no `.gitignore` para proteção contra push não intencional).

## Limites de Segurança Garantidos
Todo acesso passa pelas funções de repositório (`app/storage/repositories.py`). O `learning_policy.py` e o `audit.py` filtram ativamente `kwargs` ou `metadata` na inserção para expurgar tokens ou strings inseguras antes de efetuarem as consultas SQL.
