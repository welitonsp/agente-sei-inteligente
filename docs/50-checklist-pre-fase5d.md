# Checklist de Segurança e Maturidade: Pré-FASE 5D-S

Este checklist apresenta os critérios técnicos que devem ser validados antes de avaliar futuramente automação restrita em ambiente controlado, mediante novo PR, nova auditoria e autorização expressa na base de código.

## 1. Segurança Estrutural e Permissões
- [ ] Confirmação de que a variável `ENABLE_MINUTA_CREATION` opera bloqueada por padrão (`false`) em todas as rotinas.
- [ ] Confirmação de que as dependências do Playwright continuam encapsuladas na camada de infraestrutura (`app/sei/playwright_session.py`), mitigadas por testes para evitar acionamento direto via LLM.
- [ ] Ausência de armazenamento ou request indireto para credenciais, tokens, localStorage e senhas nos logs (`LOG_FULL_TEXT=false`).
- [ ] Termos oficiais (`assinar`, `tramitar`, `concluir`, etc.) não habilitados nesta fase e banidos do manifesto.

## 2. Homologação Manual Finalizada (FASE 5C-H)
- [ ] O relatório `homologacao_selectors.report.template.md` (ou cópia em uso local) foi preenchido de forma offline.
- [ ] Todos os seletores críticos listados no arquivo `minuta_selectors.template.json` (`process_number_area`, `include_document_button`, `document_type_search`, `document_description`, `document_access_level`, `editor_frame`, `editor_body`, `save_button`) foram inspecionados via *DevTools*.
- [ ] Os seletores não possuem `"status": "pending"`, tendo avançado para `"status": "validated"`, dependente de nova revisão humana.

## 3. Maturidade de Código e Testes
- [ ] Existência de testes automatizados que barrem injeção desautorizada de automação web (`test_script_nao_importa_libs_de_automacao` e similares).
- [ ] Suíte completa do repositório está passando (nenhum teste quebrado em `tests/`).
- [ ] A lógica central (`evaluate_phase5b_readiness`) assegura a rejeição de manifestos com campos ausentes.

## 4. Revisão Humana e Bloqueio de Atos Oficiais
- [ ] Parecer humano validou e assinou o conhecimento de que o uso não preencherá nem clicará no SEI nesta etapa, sendo sujeito a novo PR e nova auditoria.
- [ ] A autoridade responsável aprovou avaliar futuramente automação restrita em ambiente controlado, mediante novo PR, nova auditoria e autorização expressa.

## 5. Próximos Passos Pós-Checklist
Após todos os itens marcados como concluídos:
1. Abrir nova branch para a FASE 5D-S.
2. Implementar a simulação referenciando as chaves JSON validadas, estritamente em read-only e sem cliques.
3. Submeter a PR para nova rodada de revisão e auditoria.
