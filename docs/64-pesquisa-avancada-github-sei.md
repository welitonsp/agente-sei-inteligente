# Pesquisa avancada GitHub SEI - fontes para knowledge base

Data da pesquisa: 2026-07-08

## Objetivo

Mapear repositorios publicos do GitHub sobre o Sistema Eletronico de
Informacoes (SEI), SUPER, SIP, modulos oficiais, manuais, infraestrutura,
WebServices/API, IA e automacoes de comunidade, para alimentar a base de
conhecimento do Agente 19 com fontes classificadas por utilidade e risco.

Esta pesquisa nao autoriza instalacao de modulos no SEI da PMGO, uso de
credenciais, scraper autenticado, chamada a WebServices reais ou execucao de
atos oficiais. O uso e para conhecimento, arquitetura, testes controlados e
reforco das guardas de seguranca.

## Buscas executadas

Consultas principais usadas no GitHub CLI e na busca de codigo:

```text
gh search repos "SEI Sistema Eletronico de Informacoes"
gh search repos sei --owner=pengovbr --visibility=public
gh search repos sei --owner=anatelgovbr --visibility=public
gh search repos sei --owner=cgugovbr --visibility=public
gh search repos "Sistema Eletronico de Informacoes" --match=readme
gh search repos "manual SEI" --visibility=public
gh search code "ConfiguracaoSEI.php" --owner=pengovbr
gh search code "ConfiguracaoSEI.php" --owner=anatelgovbr
gh search code "WebServices" --owner=pengovbr
gh search code "swagger" --owner=pengovbr
gh search code "instalar" --owner=anatelgovbr
```

Tambem foram lidos metadados e trechos de READMEs/documentos dos repositorios
mais relevantes.

## Achado central

O GitHub nao deve ser tratado como fonte unica do "core" do SEI. A maior parte
do conhecimento publico util esta em:

1. Manuais e documentacao oficial do Processo Eletronico Nacional.
2. Modulos oficiais mantidos por PEN/Gov.br, Anatel e CGU.
3. Infraestrutura de laboratorio, Docker, Helm e imagens de desenvolvimento.
4. Documentacao de API REST via `mod-wssei`.
5. Extensoes, MCPs e automacoes de comunidade, que servem principalmente como
   estudo de UX, seletores e riscos.

## Fontes prioritarias para ingestao

| Prioridade | Repositorio | Tipo | Uso recomendado | Risco |
| --- | --- | --- | --- | --- |
| P0 | [pengovbr/pen-docs](https://github.com/pengovbr/pen-docs) | Manuais online oficiais | RAG operacional e administrativo | Baixo |
| P0 | [pengovbr/wiki-processoeletronico](https://github.com/pengovbr/wiki-processoeletronico) | Wiki PEN | RAG institucional e glossario | Baixo |
| P1 | [pengovbr/mod-wssei](https://github.com/pengovbr/mod-wssei) | API REST WSSEI | Contratos de API futura read-only | Alto se usado para execucao |
| P1 | [pengovbr/sei-docker](https://github.com/pengovbr/sei-docker) | Laboratorio Docker | Homologacao local com dados ficticios | Medio |
| P1 | [pengovbr/sei-helm](https://github.com/pengovbr/sei-helm) | Kubernetes/Helm | Entender parametros e deploy | Medio |
| P1 | [pengovbr/mod-sei-pen](https://github.com/pengovbr/mod-sei-pen) | Modulo Tramita.GOV.BR | Padrao de modulo SEI/SIP | Alto se instalado sem governanca |
| P1 | [anatelgovbr/mod-sei-ia](https://github.com/anatelgovbr/mod-sei-ia) | Modulo SEI IA | Arquitetura de modulo IA no SEI | Alto se instalado sem governanca |
| P1 | [anatelgovbr/sei-ia](https://github.com/anatelgovbr/sei-ia) | Servidor IA | Separacao modulo/servidor IA | Medio |
| P1 | [anatelgovbr/mod-sei-peticionamento](https://github.com/anatelgovbr/mod-sei-peticionamento) | Modulo oficial | Padrao de instalacao e recursos SIP | Alto |
| P1 | [anatelgovbr/mod-sei-pesquisa](https://github.com/anatelgovbr/mod-sei-pesquisa) | Pesquisa publica | Padrao de modulo publico | Alto |
| P1 | [cgugovbr/mod-sei-eouv](https://github.com/cgugovbr/mod-sei-eouv) | Integracao FalaBR | Exemplo de integracao externa | Alto |
| P2 | [SEI-Pro/mcp-seipro](https://github.com/SEI-Pro/mcp-seipro) | MCP SEI | Alerta de superficie de risco | Critico |
| P2 | [SEI-Pro/sei-pro](https://github.com/SEI-Pro/sei-pro) | Extensao navegador | Ideias de UX e seletores | Alto |
| P2 | [jonatasrs/sei](https://github.com/jonatasrs/sei) | Extensao SEI++ | Ideias de usabilidade | Alto |
| P2 | [luiscrjunior/sei-trello](https://github.com/luiscrjunior/sei-trello) | Extensao Trello | Estudo de integracao frontend | Alto |
| P2 | [franklinbaldo/sei-mcp](https://github.com/franklinbaldo/sei-mcp) | MCP comunidade | Alerta de automacao com IA | Critico |
| P2 | [zeolenon/sei-cli](https://github.com/zeolenon/sei-cli) | CLI Python | Alerta de automacao sem browser | Critico |
| Historico | [spbgovbr/sei-doc-usuario](https://github.com/spbgovbr/sei-doc-usuario) | Manual legado | Consultar apenas se `pen-docs` faltar | Baixo |
| Historico | [spbgovbr/sei-doc-admin](https://github.com/spbgovbr/sei-doc-admin) | Manual legado | Consultar apenas se `pen-docs` faltar | Baixo |

## Manuais oficiais atuais

O repositorio [pengovbr/pen-docs](https://github.com/pengovbr/pen-docs) aponta
para o portal <https://manuais.processoeletronico.gov.br/> e possui estrutura
adequada para ingestao por RAG:

1. `docs/source/SEI`: manual de usuario.
2. `docs/source/SEIADM`: administracao e parametros.
3. `docs/source/MODULOS-SEI`: documentacao de modulos.
4. `docs/source/TRAMITA.GOV.BR`: interoperabilidade.
5. `docs/source/Glossario.rst`: termos oficiais.

Arquivos do manual de usuario relevantes para o agente:

```text
SEI/Iniciando_operacoes.rst
SEI/Operacoes_basicas_com_processos.rst
SEI/Operacoes_basicas_com_documentos.rst
SEI/Operacoes_de_manutencao_e_acompanhamento_de_processos.rst
SEI/Restricao_de_acesso.rst
SEI/Usuario_externo.rst
SEI/Acompanhando_e_recuperando_informacoes_de_processos.rst
SEI/Blocos.rst
```

Para o Agente 19, esses arquivos devem entrar com metadados:

```text
fonte=oficial
tipo=manual_operacional
risco=baixo
execucao=false
uso=rag_resposta_e_classificacao
```

## Estrutura tecnica aprendida

Os modulos oficiais repetem um padrao que ajuda a entender o SEI:

1. O SEI e o SIP aparecem como bases/sistemas relacionados.
2. Modulos possuem arquivos posicionados em arvores separadas de `sei` e `sip`.
3. A ativacao do modulo passa por `sei/config/ConfiguracaoSEI.php`.
4. A chave `SEI` possui array `Modulos`, por exemplo:

```php
'SEI' => array(
    'Modulos' => array(
        'IaIntegracao' => 'ia',
    ),
),
```

5. Scripts de banco costumam ser executados via PHP CLI, separados para SIP e
   SEI.
6. O log final esperado dos scripts deve conter `FIM` e `SEM ERROS`.
7. Apos instalacao, a conferencia passa por menus como `Infra > Modulos`,
   `Infra > Parametros` e `Infra > Log`.
8. Recursos e menus sao criados no SIP e associados a perfis, com prefixos por
   modulo, como `md_ia_` e `md_pet_`.
9. Configuracoes PHP como `include_path`, `default_charset`, upload e sessao
   podem afetar modulos.

Esse conhecimento deve alimentar explicacoes e checklists, nao automacao de
instalacao.

## API e WebServices

O repositorio [pengovbr/mod-wssei](https://github.com/pengovbr/mod-wssei)
declara que o modulo WSSEI disponibiliza endpoints REST para o SEI. Achados
relevantes:

1. Documentacao de API em `docs/api.md`.
2. Swagger publicado em <https://pengovbr.github.io/mod-wssei/>.
3. Manuais de instalacao e atualizacao em `docs/`.
4. Testes funcionais da API.
5. Matriz de compatibilidade:
   - SEI/SUPER 4.0.x: mod-wssei 2.0.x.
   - SEI/SUPER 4.1.1: mod-wssei 2.2.0.
   - SEI/SUPER 5.0.x: mod-wssei 3.0.1.
6. Release mais recente observada na pesquisa: `v3.0.4`, publicada em
   2026-06-09.

Uso recomendado:

```text
fonte=oficial
tipo=contrato_api
risco=alto
execucao=false
uso=desenho_futuro_read_only
```

O agente nao deve chamar `mod-wssei` sem endpoint institucional aprovado,
credencial formal, escopo minimo e guardas independentes do LLM.

## Laboratorio e infraestrutura

Repositorios relevantes:

1. [pengovbr/sei-docker](https://github.com/pengovbr/sei-docker)
2. [pengovbr/sei-vagrant](https://github.com/pengovbr/sei-vagrant)
3. [pengovbr/sei-helm](https://github.com/pengovbr/sei-helm)
4. [pengovbr/sei5-alpine](https://github.com/pengovbr/sei5-alpine)
5. [pengovbr/sei4-alpine](https://github.com/pengovbr/sei4-alpine)
6. [pengovbr/sei-db-ref-executivo](https://github.com/pengovbr/sei-db-ref-executivo)

`sei-docker` informa documentacao de arquitetura, containers, mais de 230
variaveis de ambiente, guia de uso, orquestracao e testes. Ele serve para:

1. Laboratorio local/homologacao com dados ficticios.
2. Teste de seletores read-only.
3. Entendimento de servicos auxiliares: banco, Solr, memcached, mailcatcher,
   agendador e aplicacao web.
4. Treinamento tecnico e validacao de compatibilidade.

Nao deve ser misturado com dados reais nem com o SEI de producao.

## IA oficial no ecossistema SEI

Repositorios relevantes:

1. [anatelgovbr/mod-sei-ia](https://github.com/anatelgovbr/mod-sei-ia)
2. [anatelgovbr/sei-ia](https://github.com/anatelgovbr/sei-ia)
3. [anatelgovbr/mod-sei-stack-ia-apoio-dev](https://github.com/anatelgovbr/mod-sei-stack-ia-apoio-dev)
4. [anatelgovbr/ocr-server](https://github.com/anatelgovbr/ocr-server)

Achados principais:

1. A Anatel separa modulo PHP no SEI/SIP e servidor de solucoes de IA em
   infraestrutura propria.
2. O servidor IA e Docker/Linux e, no README, pede recursos pesados para
   producao.
3. O modulo IA exige SEI minimo 4.1.5.
4. O servidor IA depende do modulo instalado previamente.
5. Ha submodulos de similaridade de processos/documentos e assistente generativo.
6. A administracao do modulo passa por menus proprios e recursos SIP.

Impacto para o Agente 19:

1. A arquitetura externa/local continua coerente.
2. Similaridade de documentos/processos e um eixo futuro forte.
3. O agente nao precisa morar dentro do SEI para ajudar o servidor.
4. Qualquer integracao oficial demandaria governanca institucional.

## Modulos oficiais como referencia de governanca

Repositorios:

1. [pengovbr/mod-sei-pen](https://github.com/pengovbr/mod-sei-pen)
2. [pengovbr/mod-sei-protocolo-integrado](https://github.com/pengovbr/mod-sei-protocolo-integrado)
3. [pengovbr/mod-sei-estatisticas](https://github.com/pengovbr/mod-sei-estatisticas)
4. [pengovbr/mod-sei-resposta](https://github.com/pengovbr/mod-sei-resposta)
5. [anatelgovbr/mod-sei-peticionamento](https://github.com/anatelgovbr/mod-sei-peticionamento)
6. [anatelgovbr/mod-sei-pesquisa](https://github.com/anatelgovbr/mod-sei-pesquisa)
7. [cgugovbr/mod-sei-eouv](https://github.com/cgugovbr/mod-sei-eouv)

Padroes reutilizaveis no projeto:

1. Toda integracao real precisa de matriz de compatibilidade.
2. Instalar modulo e ato de administracao do SEI, nao uma decisao do agente.
3. Backup antes de mudanca e obrigatorio.
4. Separar ambiente de homologacao e producao.
5. Preferir releases oficiais a branch de desenvolvimento.
6. Registrar parametros, perfis, recursos e versao instalada.

## Comunidade, extensoes e automacoes

Repositorios uteis como estudo, mas nao como base executavel:

1. [SEI-Pro/sei-pro](https://github.com/SEI-Pro/sei-pro)
2. [jonatasrs/sei](https://github.com/jonatasrs/sei)
3. [luiscrjunior/sei-trello](https://github.com/luiscrjunior/sei-trello)
4. [SEI-Pro/mcp-seipro](https://github.com/SEI-Pro/mcp-seipro)
5. [franklinbaldo/sei-mcp](https://github.com/franklinbaldo/sei-mcp)
6. [zeolenon/sei-cli](https://github.com/zeolenon/sei-cli)
7. [rafpyprog/pySEI](https://github.com/rafpyprog/pySEI)

Uso permitido:

1. Entender funcoes que usuarios valorizam.
2. Mapear riscos de ferramentas amplas.
3. Criar cenarios adversariais de avaliacao.
4. Aprender nomes de telas, padroes visuais e classes de problema.

Uso proibido sem analise formal:

1. Copiar codigo de extensoes.
2. Armazenar usuario/senha do SEI.
3. Expor assinatura, envio, tramitacao, ciencia ou conclusao como ferramenta.
4. Usar scraper autenticado persistente.
5. Fazer login automatico.
6. Executar CLI/MCP contra SEI real.

## Regras de ingestao para a knowledge base

### Pode entrar integralmente na RAG

1. Manuais de usuario do `pen-docs`.
2. Glossario do `pen-docs`.
3. Documentacao institucional do `wiki-processoeletronico`.
4. Documentos locais ja aprovados em `knowledge_base/manual_sei`.

Metadados:

```text
risco=baixo
execucao=false
fonte=oficial
confianca=alta
```

### Entra como referencia tecnica controlada

1. `mod-wssei/docs/api.md`
2. `mod-wssei/docs/INSTALACAO.md`
3. `sei-docker/docs/*.md`
4. `sei-helm/helm/charts/sei-app/values.yaml`
5. READMEs e INSTALLs de modulos oficiais.

Metadados:

```text
risco=medio_ou_alto
execucao=false
fonte=oficial_tecnica
uso=explicacao_checklist_arquitetura
```

### Nao entra como instrucao executavel

1. MCPs com credenciais.
2. CLIs de automacao.
3. Extensoes que assinam, enviam, tramitam, criam documento ou manipulam lote.
4. Scripts de instalacao de modulo.
5. Configuracoes com senha, certificado, cookie, token ou endpoint real.

Metadados:

```text
risco=critico
execucao=false
uso=avaliacao_adversarial
```

## Atualizacao recomendada do projeto

1. Criar conector de ingestao read-only para reStructuredText (`.rst`) dos
   manuais oficiais.
2. Criar schema de fonte com campos: `repositorio`, `url`, `tipo`, `risco`,
   `licenca`, `execucao`, `prioridade`, `data_coleta`.
3. Separar colecoes RAG:
   - `sei_operacional`
   - `sei_admin`
   - `sei_api_referencia`
   - `sei_modulos_governanca`
   - `sei_riscos_automacao`
4. Ampliar os evals do agente com tentativas de:
   - pedir assinatura automatica;
   - pedir tramitacao;
   - pedir armazenamento de senha;
   - pedir uso de MCP/CLI contra SEI real;
   - pedir leitura de processo sigiloso;
   - confundir manual tecnico com permissao de execucao.

## Decisao

O conhecimento do GitHub deve fortalecer o Agente 19 como:

```text
assistente local / supervisionado / read-only por padrao / humano decide / atos oficiais bloqueados
```

As melhores fontes para alimentar o agente agora sao `pengovbr/pen-docs`,
`pengovbr/mod-wssei`, `pengovbr/sei-docker`, `pengovbr/wiki-processoeletronico`
e os modulos oficiais da Anatel/PEN/CGU apenas como referencia tecnica e de
governanca.
