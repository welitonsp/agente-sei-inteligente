# FASE 5B-H: Homologação de Seletores da Minuta

Esta documentação descreve a **FASE 5B-H** (Homologação), que tem como objetivo validar os seletores HTML necessários para a futura funcionalidade de criação de minutas no SEI Goiás.

## Importante: Apenas Homologação (Dry-run)

> [!WARNING]
> IMPORTANTE:
> - Os seletores presentes no manifesto são apenas **candidatos**.
> - O status `pending` significa que o seletor **não está homologado**.
> - **Nenhuma escrita real** está habilitada neste repositório/fase.
> - A FASE 5B (escrita real) continua sendo **futura**.


- **Sem Escrita Real:** Esta fase **NÃO** realiza nenhuma escrita real no SEI.
- **Modo Somente Leitura:** O sistema continua operando estritamente em modo de leitura (dry-run). As variáveis de ambiente `ENABLE_MINUTA_CREATION` e `ENABLE_SEI_BROWSER_AUTOMATION` permanecem como `false`.
- **Ações Oficiais Bloqueadas:** O sistema **NÃO** assina, tramita, envia, conclui, dá ciência, exclui, cancela ou libera acesso externo. Quaisquer seletores relacionados a essas ações oficiais são bloqueados pelo manifesto.
- **Nenhuma Credencial:** O sistema não guarda senhas, cookies, tokens ou sessões.

## Validação Estrutural

O módulo de homologação (`app.sei.fase5b_homologacao`) avalia um manifesto de seletores (`knowledge_base/sei_homologacao/minuta_selectors.template.json`) para verificar se todos os elementos necessários para interagir com o SEI estão mapeados e corretos.

### Observações Manuais na Tela do SEI

A homologação exige que um desenvolvedor/auditor valide manualmente no SEI:
1. Abra uma página do processo no SEI.
2. Inspecione o HTML da página usando as ferramentas de desenvolvedor do navegador.
3. Compare os seletores presentes na página real com os definidos no arquivo template.
4. Caso o seletor esteja correto, altere o status de `pending` para `validated`.

## Transição para a FASE 5B Real

A escrita real no SEI continua **bloqueada** nesta fase.
A transição para a futura **FASE 5B** (Criação de Minutas) só poderá ocorrer após:
1. Validação humana minuciosa de todos os seletores no ambiente do SEI Goiás.
2. Abertura de um **novo PR** (Pull Request) que implemente e aprove explicitamente a lógica de interação (cliques, preenchimentos) utilizando Playwright.
3. Ativação explícita da flag `ENABLE_MINUTA_CREATION` mediante autorização.
