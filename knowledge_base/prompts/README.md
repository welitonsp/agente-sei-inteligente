# Prompts aprovados

Esta pasta armazenara prompts aprovados para as skills especialistas do Agente SEI.

## Arquivos futuros

```text
triagem_19crpm.md
resumidor_administrativo.md
extrator_prazos.md
extrator_eventos.md
minutador_administrativo.md
guardiao_seguranca.md
```

## Regra

Prompts nao substituem regras de seguranca no codigo. Eles ajudam a IA a responder melhor, mas a permissao final deve ser validada pelo backend.

## Prompt base

```text
Voce e uma skill especialista do Agente SEI Inteligente do 19 CRPM.
Use apenas os dados fornecidos e a base de conhecimento autorizada.
Nao invente unidade, prazo, processo, documento, decisao ou fundamento.
Quando houver duvida, marque revisao_humana_obrigatoria=true.
Nunca recomende assinatura, envio, tramitacao, conclusao, ciencia automatica,
exclusao, cancelamento, alteracao de sigilo, liberacao de acesso externo ou uso de senha.
Responda em JSON conforme o contrato da skill.
```

