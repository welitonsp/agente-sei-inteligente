# Seletores de Referência: Automação SEI

Com base na pesquisa em repositórios open-source como o `automatiSEI` e as extensões `SEI Pro` e `SEI++`, conseguimos "aproveitar" o conhecimento comunitário sobre o mapeamento do DOM (Document Object Model) do SEI. 

Estes seletores CSS/XPath foram injetados no nosso arquivo `knowledge_base/sei_homologacao/minuta_selectors.template.json` como **propostas (status: pending)** para acelerar a Fase 5B-H. Eles ainda devem ser testados na interface real e alterados para `validated` pelo humano.

## Mapeamento Padrão Descoberto

> [!WARNING]
> IMPORTANTE:
> - Estes seletores são apenas **candidatos**.
> - O status `pending` significa que **não estão homologados**.
> - Nenhuma escrita real está habilitada neste momento.
> - A FASE 5B real continua **futura**.

| Elemento Esperado | Seletor CSS Proposto | Origem da Lógica |
| :--- | :--- | :--- |
| **Área do Número do Processo** | `#divArvoreInformacao > a` | O número do processo geralmente fica no topo da árvore de informações. |
| **Botão "Incluir Documento"** | `img[title='Incluir Documento']` | O SEI antigo baseia muitas ações em ícones de imagem (`<img>`) com atributos `title` ou `alt` específicos. |
| **Pesquisa de Tipo de Documento** | `#txtPesquisaProcedimento` | ID do campo de texto usado na tela "Gerar Documento". |
| **Opção de Tipo de Documento** | `a.classeArvore[onclick*='escolherTipoDocumento']` | Os itens da lista frequentemente usam links `<a>` com funções JavaScript inline no evento onclick. |
| **Campo "Descrição"** | `#txtDescricao` | ID padrão do input de descrição da minuta. |
| **Nível de Acesso** | `input[name='optNivelAcesso']` | Radio buttons usados para definir se é Público, Restrito ou Sigiloso. |
| **Frame do Editor de Texto** | `iframe#ifrEditor` | O SEI utiliza uma instância embutida de editor rico (ex: TinyMCE ou CKEditor). O ID do iframe onde o texto é digitado costuma ser este. |
| **Corpo do Editor** | `body.cke_editable` | A classe padrão do corpo (body) onde o texto HTML é manipulado dentro do iframe. |
| **Botão Salvar** | `#btnSalvar` | Botão primário na tela de edição do documento. |

## Próximos Passos
1. O usuário desenvolvedor deve entrar na tela do SEI manualmente (via console do desenvolvedor - F12).
2. Usar o comando `document.querySelector('SELETOR_AQUI')` para confirmar se cada um dos seletores desta tabela ainda é válido no SEI Goiás atual.
3. Atualizar o arquivo `.json` de pendente para `validated`.
