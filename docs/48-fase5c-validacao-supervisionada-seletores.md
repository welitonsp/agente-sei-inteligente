# FASE 5C-H: Coleta Manual e Validação Supervisionada de Seletores

A **FASE 5C-H** é uma fase puramente de validação e formalização (dry-run). Nela, não executamos automação no SEI. O objetivo é oficializar o conhecimento de quais elementos e seletores (CSS/XPath) do SEI serão utilizados futuramente.

## O que deve ser feito

1. Abra o navegador normalmente e faça login no SEI com a sua conta.
2. Navegue até um processo de teste que você utiliza para homologação.
3. Clique em **"Incluir Documento"**.
4. Pressione `F12` (ou botão direito -> Inspecionar) para abrir o console de desenvolvedor.
5. Inspecione os elementos alvo na página.
6. Atualize o arquivo `knowledge_base/sei_homologacao/minuta_selectors.template.json` trocando os seletores candidatos pelos seletores reais que você validou.
7. Altere o `status` de `"pending"` para `"validated"`.

## Usando o Validador Offline

Temos um script auxiliar local que **nunca se conecta à rede** nem abre o navegador. Ele simplesmente lê o seu JSON e confere se atende às regras estruturais:

```bat
.venv\Scripts\python.exe scripts\prepare_selector_homologation.py
```

Esse script listará quais seletores ainda estão `pending` ou `missing`.

## Preenchendo o Relatório de Homologação

Após concluir a revisão no JSON, preencha o documento em:
`knowledge_base/sei_homologacao/homologacao_selectors.report.template.md`

Este documento servirá de evidência (sem expor dados sensíveis) de que a validação foi executada de forma correta e humana.

## Avisos Críticos de Segurança

- A marcação `validated` em um seletor **não** significa que ele será acionado agora. O robô continua sem capacidade de clicar ou preencher o SEI.
- O relatório é **apenas uma evidência de homologação**.
- A próxima fase (**FASE 5B**, com a escrita real e Playwright injetando dados) dependerá de um novo Pull Request específico para habilitar esses seletores no Playwright.
- Nenhuma ação automática (clique, preenchimento, login, assinatura) é executada nesta fase.
