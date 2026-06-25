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
A ligação leitura→chat **já está pronta no código** (`app/sei/process_reader.py`
ligado ao `AgentChatController`), porém **inerte**: enquanto a flag estiver
desligada ou os seletores `pending`, o chat pede o texto colado. Assim que você
concluir a homologação (flag ligada + seletores `validated`), o chat passa a
**ler sozinho**: você abre o processo no SEI, manda só o **número** no chat e o
agente lê e analisa — sem copiar/colar.

Como funciona a leitura (100% read-only): o agente lê o **processo que você já
abriu** (não digita nem clica para abrir), confere se o número confere e lê a
árvore + o conteúdo visível pela `ReadOnlyPage`. Se o processo aberto não bater
com o número enviado, ele avisa.
