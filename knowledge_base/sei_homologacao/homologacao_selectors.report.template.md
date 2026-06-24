# Relatório de Homologação de Seletores (FASE 5C-H)

**Data da Homologação:** [DD/MM/AAAA]  
**Responsável pela Homologação:** [Nome do Desenvolvedor/Auditor]  
**Ambiente:** Homologação / Manual (Dry-run)

> [!WARNING]
> **AVISO DE SEGURANÇA:** Este relatório é apenas uma evidência de coleta e inspeção manual dos seletores. O preenchimento ou a aprovação deste relatório **NÃO** habilita a escrita real no SEI. Nenhuma ação automática é executada no SEI. A FASE 5B (escrita real) continua sendo futura.

## 1. Seletores Inspecionados

| Elemento SEI | Seletor CSS | Status | Evidência (Não Sensível) |
| :--- | :--- | :--- | :--- |
| `process_number_area` | `[Preencher]` | `pending` / `validated` | `Ex: Encontrado na div do cabeçalho` |
| `include_document_button` | `[Preencher]` | `pending` / `validated` | `Ex: Botão com ícone verde` |
| `document_type_search` | `[Preencher]` | `pending` / `validated` | `Ex: Input text de pesquisa` |
| `document_type_option` | `[Preencher]` | `pending` / `validated` | `Ex: Opção retornada na lista` |
| `document_description` | `[Preencher]` | `pending` / `validated` | `Ex: Campo textarea de descrição` |
| `document_access_level` | `[Preencher]` | `pending` / `validated` | `Ex: Radio button de acesso público` |
| `editor_frame` | `[Preencher]` | `pending` / `validated` | `Ex: Iframe do CKEditor` |
| `editor_body` | `[Preencher]` | `pending` / `validated` | `Ex: Body editável interno ao iframe` |
| `save_button` | `[Preencher]` | `pending` / `validated` | `Ex: Botão de salvar no canto direito` |

## 2. Checklist de Segurança

- [ ] Todos os seletores listados acima foram testados usando `document.querySelector` no console do navegador?
- [ ] O relatório e os seletores NÃO contêm senhas, cookies ou dados sensíveis do processo?
- [ ] O manifesto JSON (`minuta_selectors.template.json`) foi atualizado para refletir o status `validated` apenas dos itens aprovados?
- [ ] A flag `ENABLE_MINUTA_CREATION` permanece igual a `false` no seu `.env`?

## 3. Decisão

**Aprovado para avançar à próxima fase (FASE 5B real)?**
[ ] SIM  
[ ] NÃO  

**Observações Finais:**
[Adicionar observações se houver]

---
*(Lembrete: a próxima fase, caso aprovada, ainda dependerá de um novo Pull Request implementando as ações do Playwright associadas a esses seletores)*.
