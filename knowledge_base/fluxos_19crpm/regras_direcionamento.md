# Regras de direcionamento

Substituir os exemplos abaixo pelas regras reais do 19 CRPM.

## Formato recomendado

```text
Regra:
Quando:
Entao:
Unidade sugerida:
Prioridade:
Revisao humana:
Justificativa:
```

## Exemplos

```text
Regra: exemplo-evento-operacional
Quando: assunto contem "evento operacional" e local pertence a area da unidade X
Entao: sugerir unidade X
Unidade sugerida: EXEMPLO
Prioridade: normal
Revisao humana: true
Justificativa: exemplo, nao usar em producao sem substituir por regra real
```

## Regra de seguranca

Se nenhuma regra real se aplicar, o agente deve retornar:

```text
unidade_sugerida: ""
revisao_humana_obrigatoria: true
motivo: "Nao ha regra suficiente para definir a unidade responsavel."
```
