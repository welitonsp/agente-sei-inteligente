# Pesquisa sobre agentes de IA para SEI

Data da pesquisa: 2026-06-21

## Resultado geral

Ja existem iniciativas reais de IA integradas ou relacionadas ao SEI. As principais encontradas foram:

1. SEI IA, desenvolvido pela Anatel.
2. ANIA, desenvolvida pelo Tribunal de Contas do Estado de Sao Paulo.
3. SEI Pro, extensao/ferramenta nao institucional para uso de ChatGPT no editor do SEI.

O aprendizado principal para o projeto do 19 CRPM e que a IA deve atuar como assistente do servidor autenticado, nao como usuario unico centralizado.

## SEI IA - Anatel

Fontes:

1. https://www.gov.br/anatel/pt-br/assuntos/noticias/anatel-inova-com-inteligencia-artificial-no-sistema-eletronico-de-informacoes
2. https://www.gov.br/anatel/pt-br/assuntos/noticias/anatel-aprimora-o-assistente-de-ia-do-sei-para-transformar-e-modernizar-suas-rotinas-administrativas
3. https://github.com/anatelgovbr/mod-sei-ia
4. https://github.com/anatelgovbr/sei-ia

### O que e

O SEI IA e um modulo integrado ao SEI, criado pela Anatel. Ele inclui:

1. Assistente baseado em IA generativa.
2. Recomendacao de processos similares.
3. Recomendacao de documentos similares.
4. Classificacao de processos por ODS.

O reposititorio `sei-ia` descreve um servidor de solucoes de IA com dois submodulos principais:

1. `SEI-IA-SIMILARIDADE`.
2. `SEI-IA-ASSISTENTE`.

### Ponto tecnico importante

O SEI IA oficial exige instalacao no ambiente SEI, modulo SEI IA previamente instalado e configurado, e servidor Linux com Docker. A documentacao do repositorio informa requisitos elevados, como CPU de 16 cores e 128 GB de RAM para o servidor de IA.

Isso indica que, para uso oficial pleno, o caminho correto e institucional: administrador do SEI, instalacao de modulo, configuracao de perfis e infraestrutura propria.

### O que podemos aprender

1. Integrar IA dentro do SEI e melhor para respeitar permissoes do proprio sistema.
2. O assistente deve ficar disponivel conforme perfil/permissao do usuario.
3. O modulo deve ser administrado por perfis, nao por um login unico compartilhado.
4. A IA deve interagir com documentos/processos que o usuario ja pode acessar.
5. A solucao precisa de letramento e uso seguro de IA.

## ANIA - TCESP

Fontes:

1. https://www.tce.sp.gov.br/6524-artigo-ania-revolucao-inteligencia-artificial-tcesp
2. https://www.labtcs.com.br/boa-pratica/ania
3. https://www.tceto.tc.br/tceto-firma-cooperacao-com-tribunal-de-contas-de-sao-paulo-para-uso-de-inteligencia-artificial/
4. https://www.portalseibahia.saeb.ba.gov.br/noticias/2024-10-25/sei-bahia-vai-passar-contar-com-recursos-inteligencia-artificial

### O que e

A ANIA e uma Assistente Natural com Inteligencia Artificial criada pelo TCESP. Ela foi descrita como ferramenta para analise de documentos PDF, perguntas em linguagem natural, resumos, estruturacao de topicos e apoio a redacao. Tambem ha referencias a modulos como `ANIA.pdf`, `ANIA.legis`, `ANIA.dados`, `ANIA.chat` e `ANIA.sei`.

Noticias de outros orgaos indicam compartilhamento por acordo de cooperacao para uso com SEI.

### O que podemos aprender

1. A solucao nasceu modular.
2. Comecou com analise de PDF antes de uma integracao mais profunda.
3. Foi pensada para ambiente controlado, com privacidade.
4. Entrou como apoio ao servidor, nao como decisor administrativo.
5. Pode ser caminho institucional se houver acordo de cooperacao viavel.

## SEI Pro

Fonte:

1. https://sei-pro.github.io/sei-pro/pages/FERRAMENTASIA.html

### O que e

Ferramenta que adiciona funcoes ao SEI e permite uso de ChatGPT no editor de documentos com prompts prontos.

### Alerta

A propria pagina alerta que dados sao processados por servico externo e orienta nao enviar informacoes restritas ou sigilosas.

### O que podemos aprender

1. Prompts prontos ajudam o usuario.
2. Integracao no editor e pratica, mas exige controle de dados.
3. Para nosso projeto, esse caminho isolado nao e suficiente para seguranca institucional.

## Conclusao da pesquisa

Nao devemos criar um agente que acessa o SEI com um unico usuario. Isso quebraria a rastreabilidade individual, confundiria responsabilidade administrativa e criaria risco grave.

A arquitetura correta para o 19 CRPM deve seguir um destes modelos:

1. Modelo institucional integrado: instalar/adotar SEI IA oficial, se o orgao gestor do SEI permitir. Decisao atual: indisponivel.
2. Modelo assistido por sessao: nosso agente roda na estacao do servidor, usando somente a sessao SEI que ele abriu manualmente.
3. Modelo externo sem login no SEI: agente processa e-mail, PDF, agenda, Telegram e minutas fora do SEI; o servidor copia/revisa/pratica atos no SEI manualmente.

Para o projeto atual, o caminho mais seguro e iniciar no modelo 3 e evoluir para o modelo 2 apenas para leitura assistida. O modelo 1 esta descartado no momento por inviabilidade de instalacao do modulo oficial.
