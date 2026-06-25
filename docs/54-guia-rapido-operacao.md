# Guia rápido — como usar o Agente 19 com o SEI

Orientação prática para o dia a dia. O Agente 19 é um **assistente local
supervisionado**: ele **não** controla seu navegador, **não** captura senha/
sessão e **nunca** assina, envia ou tramita. O modelo é **copiar-e-colar**.

## Princípio
> Você loga no SEI normalmente → **você** copia o texto ou exporta o PDF → cola
> no painel do Agente 19 → ele analisa **localmente** (offline) → devolve resumo,
> prazo, providência e minuta → **você** copia de volta ao SEI e pratica o ato
> oficial manualmente.

## Passo a passo

1. **Abrir o Agente 19** (terminal, na pasta do projeto):
   ```
   python -m app.desktop
   ```
   Abre uma janela com dois lados: **SEI oficial** e **Agente 19**.
   *(Alternativa só-web: `python -m app.dashboard` → `http://127.0.0.1:8000`.)*

2. **Logar no SEI:** botão **“Abrir SEI oficial”** → faça o login na página
   oficial. O agente não participa do login.

3. **Pegar o conteúdo** do documento aberto no SEI:
   - **Copiar texto** → colar no campo “Texto copiado”; **ou**
   - **Exportar PDF** pelo SEI → “Selecionar PDF” no painel.

4. **Preencher** (opcional): nº do **Processo SEI**, **Operador local** (seu
   nome, não é usuário do SEI), **Título**.

5. **“Analisar texto”** (ou **“Analisar PDF”**) → o agente devolve, read-only:
   - **Tipo provável** (ofício, despacho, intimação…)
   - **Resumo** estrutural (sem persistir o texto integral)
   - **Prazo** identificado — inclusive **relativos** ("no prazo de 10 dias
     úteis") com **data-limite calculada**
   - **Providência sugerida** + **confiança**

6. **(Opcional) “Triagem local”** → sugere unidade de destino do 19 CRPM pelas
   regras da base de conhecimento.

7. **(Opcional) “Gerar minuta”** → rascunho de despacho/ofício para revisão.

8. **“Copiar resultado”** → cole no SEI, **revise, edite e só então assine/
   tramite você mesmo**.

## O que ele NÃO faz (limites por design)
- Não clica em botões do SEI nem preenche formulários sozinho.
- Não assina, envia, tramita, conclui nem dá ciência.
- Não guarda senha nem usa conta compartilhada.
- PDF digitalizado/sem texto → avisa “OCR necessário” e para.

## IA Claude (opcional, desligada por padrão)
A análise é 100% local por padrão (custo zero, offline). Para usar o Claude,
configure no `.env` **local**:
```
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-…
SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT=true   # só se aceitar enviar conteúdo do SEI
```
Sem essas linhas, nada do SEI sai do seu computador. Ver
[docs/53](53-camada-ia-claude.md).

## Erros comuns
| Situação | O que fazer |
|---|---|
| PDF sem texto | Exportar PDF pesquisável ou ler manualmente |
| Data/prazo ambíguo | Revisar manualmente antes de agendar |
| Ação SEI proibida | O guard bloqueia e registra log; faça o ato manualmente |
