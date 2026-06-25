# Homologação da leitura automática (FASE 5C — Frente 2)

Objetivo: permitir que o Agente 19 **leia** um processo aberto pela sua sessão
logada (sem você precisar copiar/colar). Isto é **100% leitura** — nunca clica,
preenche ou escreve. Antes de habilitar, homologamos os **seletores reais** do
SEI com você, de forma supervisionada.

> Esta frente fica **desligada por padrão** (`ENABLE_SEI_BROWSER_AUTOMATION=false`).
> A homologação é feita por você, logado, na sua máquina.

## Passo a passo (você executa)

### 1. Instalar o Playwright (uma vez)
```
pip install playwright
playwright install chromium
```

### 2. Ligar a flag no `.env` local
```
ENABLE_SEI_BROWSER_AUTOMATION=true
```
(Continua sem qualquer permissão de escrita — só leitura.)

### 3. Rodar a homologação supervisionada
```
python scripts/homologate_read_selectors.py
```
- Abre um navegador efêmero na URL **oficial** do SEI.
- **Você** faz o login e abre um processo.
- Volte ao terminal e tecle **ENTER**.
- O script relata, **somente leitura**: título da página, URL, números de
  processo visíveis e os itens lidos da **árvore de documentos**.

Se a flag estiver desligada, o script **se recusa** a abrir o navegador.

### 4. Confirmar os seletores reais
Com o processo aberto, inspecione (F12) e confirme os seletores reais em
`knowledge_base/sei_homologacao/read_selectors.template.json`. Ajuste o `value`
de cada um e mude o `status` de `pending` para `validated`.

Seletores a confirmar:
| Chave | O que é |
|---|---|
| `process_search_box` | Caixa para abrir o processo pelo número |
| `process_number_label` | Onde aparece o número do processo aberto |
| `document_tree` | Árvore de documentos do processo |
| `document_content_frame` | Iframe de visualização do documento |
| `document_content_body` | Corpo visível do documento |

### 5. Validar o manifesto (dry-run, sem navegador)
```
python scripts/validate_read_selectors.py
```
Deve mostrar **[OK] valido** quando todos os seletores estiverem `validated` e
nenhum apontar para ato oficial.

## Garantias de segurança
- Leitura por `ReadOnlyPage`: sem métodos de clique/preenchimento/navegação.
- Seletores que mencionem assinar/enviar/tramitar/concluir/excluir são
  **bloqueados** pelo validador.
- Sessão Playwright **efêmera** (sem perfil persistente), aberta só na URL
  oficial; o login é seu e a senha nunca é capturada.
- Nada é escrito no SEI. A criação de documento (Frente 3 / FASE 5B) é uma fase
  seguinte e separada, que exige autorização expressa.

## Depois da homologação
Com os seletores `validated`, conectamos a leitura ao chat (frente 1): você
manda só o **número** e o agente busca e analisa o processo — sem copiar/colar.
Esse passo de ligação eu faço no código, após a sua homologação.
