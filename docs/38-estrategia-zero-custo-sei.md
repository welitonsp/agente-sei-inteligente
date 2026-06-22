# Fase 38 - Estrategia zero custo para leitura, analise e minuta SEI

Data: 2026-06-22
Status: PLANEJADA

## Regra financeira

O projeto deve operar com custo zero por padrao. Nao usar servico pago,
assinatura mensal, API paga por token, ferramenta RPA paga, hospedagem paga ou
produto que gere dependencia financeira.

Servicos externos so podem ser usados quando:

1. ja existirem na estrutura institucional;
2. tiverem cota gratuita suficiente;
3. nao exigirem cartao de credito;
4. forem autorizados pelo responsavel;
5. nao receberem conteudo real do SEI sem autorizacao formal.

## Estrategia recomendada

### Fase 38.1 - Manual seguro, custo zero

- [ ] Usuario abre o SEI manualmente.
- [ ] Usuario baixa/exporta PDF manualmente.
- [ ] Usuario envia PDF/texto ao Agente 19 Desktop.
- [ ] Agente analisa localmente.
- [ ] Agente informa do que se trata.
- [ ] Agente sugere se a resposta parece oficio, despacho, encaminhamento ou informacao.
- [ ] Agente sugere texto preliminar fora do SEI.
- [ ] Usuario revisa, copia e cria manualmente no SEI.
- [ ] Usuario assina/tramita apenas se decidir.

Essa fase e a mais segura e barata. Ja pode evoluir a partir do desktop atual.

### Fase 38.2 - OCR e classificacao local

- [ ] Implementar OCR gratuito para PDF escaneado.
- [ ] Usar motor local gratuito quando disponivel, como Tesseract instalado na maquina.
- [ ] Criar classificadores por regra, sem IA paga.
- [ ] Usar palavras-chave e knowledge base local do 19 CRPM.
- [ ] Gerar minuta por templates locais.
- [ ] Exigir revisao humana em todas as respostas.

### Fase 38.3 - IA local opcional

- [ ] Avaliar modelo local gratuito apenas se o computador suportar.
- [ ] Rodar modelo na maquina local, sem enviar conteudo do SEI para nuvem.
- [ ] Usar IA local como auxiliar, nunca como autoridade final.
- [ ] Manter fallback por regras/templates caso o modelo local seja lento ou inviavel.

Exemplos de abordagem gratuita possivel: modelos locais abertos via ferramenta
local instalada na maquina. Isso depende de hardware e autorizacao para instalar
software.

### Fase 38.4 - Leitura SEI read-only autorizada

- [ ] Somente com autorizacao institucional.
- [ ] Preferir API/WebServices oficiais de leitura, se existirem e forem liberados.
- [ ] Se nao houver API, manter exportacao manual de PDF.
- [ ] Nao usar login/senha dentro do Agente 19.
- [ ] Nao capturar cookie, sessao, token ou localStorage.
- [ ] Nao automatizar cliques sem homologacao formal.

### Fase 38.5 - Criacao assistida de minuta no SEI

- [ ] Somente depois de homologacao/autorizacao.
- [ ] Criar apenas minuta/rascunho, nunca assinar.
- [ ] Exigir aprovacao humana antes de criar.
- [ ] Registrar auditoria local.
- [ ] Permitir que o analista revise e assine manualmente no SEI.

Sem autorizacao, a alternativa segura e custo zero continua sendo copiar o texto
gerado pelo Agente 19 e colar manualmente no SEI.

## O que o Agente 19 deve sugerir

- [ ] Resumo do processo.
- [ ] Tipo provavel da demanda.
- [ ] Prazo/evento, quando houver.
- [ ] Unidade provavel, somente se houver regra real na knowledge base.
- [ ] Se a resposta tende a ser oficio, despacho, informacao, encaminhamento ou ciencia.
- [ ] Texto preliminar.
- [ ] Pendencias antes da decisao.
- [ ] Nivel de confianca.

## O que nao deve fazer

- [ ] Comprar ou assinar servico.
- [ ] Usar API paga.
- [ ] Enviar conteudo real do SEI para IA externa.
- [ ] Pedir usuario ou senha do SEI.
- [ ] Capturar cookie/sessao/token.
- [ ] Automatizar clique no SEI sem homologacao.
- [ ] Assinar.
- [ ] Tramitar.
- [ ] Enviar processo.
- [ ] Concluir processo.

## Stack zero custo recomendada

| Necessidade | Opcao zero custo |
| --- | --- |
| Aplicacao local | Python + Tkinter/stdlib |
| Backend local | Python stdlib/FastAPI se ja aceito |
| Banco | SQLite |
| PDF pesquisavel | `pypdf` |
| OCR | Tesseract local, quando instalado/autorizado |
| Regras/classificacao | Python + arquivos locais em Markdown/CSV |
| Minutas | Templates Markdown/texto local |
| IA | Modelo local gratuito opcional, conforme hardware |
| Agenda | Google existente/dry-run, sem contratar servico |
| Alertas | Telegram gratuito, se autorizado |

## Proxima entrega tecnica sugerida

Implementar primeiro o **minutador por templates locais**, sem IA paga:

1. criar knowledge base minima do 19 CRPM;
2. criar templates de oficio, despacho, informacao e encaminhamento;
3. classificar o tipo provavel por regras;
4. gerar texto preliminar;
5. mostrar confianca e pendencias;
6. copiar resultado para uso manual no SEI.
