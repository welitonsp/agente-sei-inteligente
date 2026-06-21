# Fluxos 19 CRPM

Esta pasta deve armazenar as regras internas que permitem ao agente filtrar processos e documentos de interesse do 19 CRPM.

## Arquivos futuros

```text
unidades_19crpm.csv
unidades_alto_comando.csv
regras_direcionamento.md
palavras_chave_19crpm.md
modelos_resposta.md
```

Os arquivos acima ja existem como templates. Eles devem ser preenchidos com dados reais antes de ativar a triagem automatica.

## Dados necessarios

Para o robozinho SEI funcionar corretamente, precisamos cadastrar:

1. Unidades pertencentes ao 19 CRPM.
2. Unidades de Alto Comando relevantes.
3. Assuntos que geram providencia.
4. Assuntos meramente informativos.
5. Regras para escolher a unidade responsavel.
6. Modelos de minuta por tipo de demanda.

## Regra

O agente nao deve inventar direcionamento. Se nao houver regra suficiente para escolher uma unidade, deve marcar como `revisao_humana_obrigatoria`.
