# FASE 5D-S: Simulação Operacional Ponta a Ponta

A **FASE 5D-S** representa o penúltimo passo de segurança antes da futura e bloqueada fase de inserção mecânica (FASE 5D). Nesta fase construímos um "motor simulador" (`app/sei/fase5d_simulacao.py`) que processa todos os requisitos da futura escrita de minuta (cadastro de negócio + manifesto JSON validado) e cospe um **plano de ação simulado**, sem jamais interagir com navegadores.

## Premissas de Segurança Desta Fase
- **FASE 5D-S é apenas simulação offline.**
- **Não** é escrita real.
- **Não** acessa o SEI automaticamente.
- **Não** clica em botões nem avalia DOM.
- **Não** preenche formulários.
- **Não** salva minutas nem documentos.
- **Não** executa atos oficiais (assinar, tramitar, concluir, enviar, dar ciência).
- `ENABLE_MINUTA_CREATION=false` permanece **obrigatório** em qualquer `.env`.

## Como executar a simulação local

No terminal do repositório, rode o script offline que monta o cenário com um processo fictício e processa seu JSON de seletores atual:

```bat
.\.venv\Scripts\python.exe scripts\simulate_phase5d_operation.py
```

Você verá a saída listando as etapas simuladas de validação, como `[SIMULATED_SELECTOR_CHECK]`, garantindo que nenhuma operação real foi executada.

## Formalizando a Simulação
Após a verificação no console, o desenvolvedor/auditor preenche o relatório de prontidão contido em:
`knowledge_base/sei_homologacao/fase5d_simulacao.report.template.md`

## O Que Vem Depois?
A FASE 5D-S **NÃO** habilita a FASE 5B ou 5D real de imediato.
Qualquer tentativa de transformar as etapas em automação web exigirá novo PR, nova auditoria e autorização expressa.

