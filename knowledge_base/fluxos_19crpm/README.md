# Knowledge base local do 19 CRPM

Esta pasta guarda regras locais e gratuitas para triagem, roteamento e escolha
de minuta.

Regra de seguranca:

1. Nao preencher com dados sensiveis reais sem revisao.
2. Nao inventar unidade.
3. Se uma regra nao existir ou estiver ambigua, o sistema deve responder
   `indefinido` e exigir revisao humana.
4. Toda regra real deve ser revisada pelo responsavel do projeto.

Arquivos:

- `unidades_19crpm.csv`: unidades internas que podem receber providencia.
- `unidades_alto_comando.csv`: unidades externas/alto comando relevantes.
- `palavras_chave_19crpm.csv`: palavras-chave para identificar interesse.
- `regras_direcionamento.csv`: regras que sugerem unidade, tipo de minuta e providencia.
- `modelos_resposta.md`: orientacoes locais para respostas.
