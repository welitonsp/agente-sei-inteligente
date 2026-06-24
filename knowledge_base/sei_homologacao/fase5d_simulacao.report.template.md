# Relatório de Simulação Operacional (FASE 5D-S)

**Data da Simulação:** [DD/MM/AAAA]  
**Responsável:** [Nome do Desenvolvedor/Auditor]  
**Ambiente:** Simulação Offline (Dry-run isolado)

> [!WARNING]
> **AVISO DE SEGURANÇA:** Este relatório atesta o sucesso ou falha da lógica de montagem do plano de execução do robô. A FASE 5D-S não clica, não preenche, não acessa rede e não altera o SEI. **A próxima etapa de automação restrita dependerá obrigatoriamente de novo PR, nova auditoria e autorização expressa.**

## 1. Dados de Entrada Simulados

**Manifesto Utilizado:** `minuta_selectors.template.json`  
**Cadastro Simulado:**
- **Processo:** `[Preencher]`
- **Tipo de Documento:** `[Preencher]`
- **Nível de Acesso:** `[Preencher]`
- **Descrição:** `[Preencher]`

## 2. Resultado da Validação

**Validação do Cadastro:** `[OK / FALHA]`  
**Validação do Manifesto:** `[OK / FALHA]`  
**Blockers:** `[Nenhum / Listar blockers]`  

## 3. Plano Operacional Simulado

Caso as validações tenham passado, o motor gerou a seguinte sequência de passos puramente simulados (ações tipo `simulated_selector_check`, `simulated_field_mapping`, etc):

| Passo | Ação Simulada | Seletor Alvo | Dados |
|:---|:---|:---|:---|
| 1 | `[Ação]` | `[Seletor]` | `[Dados se houver]` |
| 2 | `[Ação]` | `[Seletor]` | `[Dados se houver]` |
| 3 | `[Ação]` | `[Seletor]` | `[Dados se houver]` |
| ... | ... | ... | ... |

## 4. Garantias e Decisão Final

- **Operação real habilitada?** NÃO
- **Nenhuma operação real foi executada?** SIM
- **O script fez chamadas de rede?** NÃO

**Decisão Final:**
A simulação foi concluída com sucesso e cobre todas as variáveis de negócio sem vazar escopo de execução?
[ ] SIM
[ ] NÃO

**Observação:** qualquer automação futura exige novo PR, nova auditoria e autorização expressa.
