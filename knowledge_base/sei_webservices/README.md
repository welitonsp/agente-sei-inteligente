# SEI WebServices

Fonte local:

```text
d:\MEUS DOCUMENTOS\Downloads\SEI-WebServices-v4.0.pdf
```

Uso no agente:

1. Referencia tecnica de integracao.
2. Apoio para desenho de cliente SEI futuro.
3. Classificacao de operacoes permitidas, restritas e proibidas.

Classificacao:

```text
fonte=manual_tecnico
risco=alto
uso=consulta_controlada
execucao=false
```

Regra:

O conteudo deste manual nao autoriza execucao automatica. Qualquer integracao SEI deve passar por `app/core/permissions.py` e `app/sei/sei_action_guard.py`.

Operacoes de escrita ou alteracao ficam bloqueadas por padrao. A base WebServices deve ser usada para entender limites tecnicos e consultas autorizadas, nao para automatizar atos oficiais.
