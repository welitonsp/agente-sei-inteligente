# Regras de Git, IA, Commit, Push, PR e Merge

## Objetivo

Definir regras para desenvolvimento com apoio de IA no projeto Agente SEI Inteligente - 19 CRPM, garantindo rastreabilidade, revisao humana, seguranca e qualidade tecnica.

## Principio central

IA pode ajudar a escrever, revisar, testar e documentar codigo. IA nao substitui responsabilidade humana pelo commit, push, pull request ou merge.

Todo codigo gerado ou alterado com apoio de IA deve ser:

1. Revisado por humano.
2. Testado.
3. Explicavel.
4. Rastreavel.
5. Seguro para o contexto SEI.

## Regras de branch

Nao desenvolver direto na `main`, exceto alteracao documental pequena e autorizada pelo chefe do projeto.

Padrao de branch:

```text
codex/<tipo>-<descricao-curta>
```

Tipos:

```text
docs
feature
fix
security
test
refactor
chore
```

Exemplos:

```text
codex/feature-fundacao-tecnica
codex/security-guardiao-sei
codex/test-permissoes
codex/docs-regras-git-ia
```

## Regras de commit

### Commit deve ser pequeno e coerente

Cada commit deve representar uma unidade logica de mudanca.

Bom:

```text
Adiciona guardiao de acoes do SEI
Cria testes de permissoes proibidas
Documenta politica de dados do SEI
```

Ruim:

```text
varias coisas
update
ajustes
codigo novo
```

### Padrao de mensagem

Formato:

```text
<verbo no presente> <objeto da mudanca>
```

Exemplos:

```text
Cria estrutura inicial do app
Adiciona modelo de auditoria
Bloqueia acoes oficiais no guardiao
Implementa leitura de PDF local
Corrige contrato da skill de prazos
```

### Commits proibidos

Nao commitar:

1. `.env` real.
2. Senhas.
3. Tokens.
4. Cookies.
5. Banco SQLite com dados reais.
6. PDFs reais do SEI.
7. HTML completo de pagina do SEI.
8. Dados pessoais nao anonimizados.
9. Arquivos temporarios.
10. Codigo que permita ato oficial no SEI sem guardiao.

## Checklist antes do commit

Antes de commitar, verificar:

```text
git status -sb
git diff
```

Checklist:

| Item | Obrigatorio |
| --- | --- |
| Mudanca tem escopo claro | Sim |
| Nao ha segredo real | Sim |
| Nao ha dado real do SEI | Sim |
| Testes relevantes foram rodados | Sim, quando houver codigo |
| Documentacao foi atualizada | Sim, se mudar regra/contrato |
| Guardiao de seguranca nao foi enfraquecido | Sim |
| Acoes proibidas continuam bloqueadas | Sim |

## Regras de push

Push deve ser feito para branch de trabalho.

Padrao:

```text
git push -u origin <branch>
```

Push direto para `main`:

1. Permitido apenas para documentacao administrativa simples, enquanto o projeto estiver sem codigo de producao.
2. Proibido apos criacao de codigo de aplicacao.
3. Proibido para alteracao de seguranca, permissoes, SEI, IA, banco, integracoes ou dados.

## Regras de Pull Request

Todo desenvolvimento de codigo deve entrar por PR.

Titulo:

```text
[tipo] descricao curta
```

Exemplos:

```text
[feature] fundacao tecnica do backend
[security] guardiao de acoes do SEI
[test] permissoes proibidas
[docs] regras de git e IA
```

## Template de PR

Todo PR deve conter:

```markdown
## Objetivo

Explique a mudanca.

## Escopo

- Arquivos/modulos alterados
- O que ficou fora

## Uso de IA

- IA usada? Sim/Nao
- Para que foi usada?
- O que foi revisado manualmente?

## Segurança SEI

- Altera permissoes? Sim/Nao
- Toca em SEI? Sim/Nao
- Pode executar ato oficial? Nao
- Guardiao testado? Sim/Nao

## Dados

- Usa dado real? Nao
- Usa dado anonimo? Sim/Nao
- Envia dado para IA externa? Nao

## Testes

- Comandos executados
- Resultado

## Evidencias

- Prints, logs ou saidas relevantes, quando aplicavel

## Checklist

- [ ] Nao inclui segredo
- [ ] Nao inclui dado real do SEI
- [ ] Acoes proibidas continuam bloqueadas
- [ ] Testes relevantes passaram
- [ ] Documentacao atualizada
```

## Regras de review

Todo PR de codigo deve ter revisao humana antes do merge.

Revisor deve verificar:

1. Escopo.
2. Segurança.
3. Testes.
4. Contratos JSON.
5. Logs e auditoria.
6. Ausencia de segredos.
7. Ausencia de dados reais.
8. Aderencia a matriz de conformidade.

## Regras de merge

Merge so pode acontecer quando:

1. PR revisado.
2. Testes passando.
3. CI passando.
4. Sem segredo detectado.
5. Sem dado real do SEI.
6. Sem enfraquecer guardiao.
7. Sem alterar regra de ouro sem aprovacao do chefe do projeto.

Merge proibido quando:

1. Teste de permissao falhar.
2. PR permitir assinatura, envio, tramitacao, conclusao, ciencia automatica, exclusao ou cancelamento.
3. PR guardar senha, cookie ou token.
4. PR enviar conteudo real do SEI para IA externa.
5. PR implementar navegacao automatica no SEI sem autorizacao formal.
6. PR alterar politica de dados sem revisao.

## Estrategia de merge

Recomendacao:

```text
Squash merge
```

Motivo:

1. Mantem historico limpo.
2. Agrupa commits pequenos em uma entrega logica.
3. Facilita auditoria.

Excecao:

Usar merge commit apenas quando for importante preservar historico de multiplos commits tecnicos.

## Regras especificas para codigo gerado por IA

Codigo gerado por IA deve passar por revisao reforcada.

Obrigatorio:

1. Ler o codigo antes de commitar.
2. Remover trechos desnecessarios.
3. Verificar imports e dependencias.
4. Verificar tratamento de erro.
5. Verificar logs sem dados sensiveis.
6. Testar caminho feliz e caminho de erro.
7. Testar seguranca quando tocar em permissoes.

Proibido aceitar codigo de IA que:

1. Guarde senha.
2. Leia `.env` e imprima segredo em log.
3. Clique em botoes do SEI.
4. Ignore `sei_action_guard.py`.
5. Envie dados reais para API externa.
6. Crie permissao ampla sem lista positiva.
7. Faça `except Exception: pass` em fluxo critico.

## Regras de CI obrigatorias

Quando o codigo existir, o GitHub Actions deve rodar:

1. Testes unitarios.
2. Testes de permissoes proibidas.
3. Testes de contratos JSON das skills.
4. Checagem de segredos.
5. Lint/format.

Gate minimo antes de integrar Agenda, Telegram, IA ou SEI:

```text
tests/test_permissions.py
tests/test_sei_action_guard.py
tests/test_contracts.py
```

## Protecao de branch

Quando houver codigo de aplicacao, configurar protecao da `main`:

1. Exigir PR.
2. Exigir CI verde.
3. Exigir pelo menos 1 aprovacao.
4. Bloquear force push.
5. Bloquear exclusao da branch.
6. Exigir branch atualizada antes do merge.

## Politica de releases

Versoes:

```text
v0.1-docs
v0.2-fundacao-tecnica
v0.3-painel-mvp
v0.4-pdf-texto
v0.5-agenda-telegram
v1.0-operacao-assistida
```

Cada release deve ter:

1. Changelog.
2. Escopo.
3. Riscos conhecidos.
4. Testes executados.
5. Decisao de liberacao.

## Decisao atual

Enquanto o projeto estiver documental:

1. Commits diretos na `main` sao aceitaveis para documentacao.
2. Codigo de aplicacao deve entrar por branch e PR.
3. Qualquer alteracao envolvendo SEI, seguranca, IA externa, dados reais ou credenciais deve passar por PR e revisao.

