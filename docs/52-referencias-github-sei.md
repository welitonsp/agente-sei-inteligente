# Referencias GitHub do SEI - Estudo e aprendizados aplicaveis

Data da revisao: 2026-06-29

## Objetivo

Mapear repositorios publicos do GitHub desenvolvidos para o SEI/SUPER/Tramita
GOV.BR, identificar padroes tecnicos reutilizaveis e decidir o que pode ou nao
ser aproveitado no Agente 19.

Esta pesquisa nao autoriza instalacao de modulo no SEI da PMGO, automacao de
login, uso de credenciais, webservices reais ou copia de codigo de terceiros.
O objetivo e aprendizado arquitetural.

## Matriz de repositorios relevantes

| Repositorio | Organizacao | Tipo | Utilidade para o Agente 19 | Decisao |
| --- | --- | --- | --- | --- |
| [pengovbr/mod-wssei](https://github.com/pengovbr/mod-wssei) | PEN/Gov.br | Modulo REST WSSEI | Referencia principal de API REST oficial para SEI/SUPER | Estudar contratos e Swagger; nao usar sem endpoint autorizado |
| [pengovbr/sei-docker](https://github.com/pengovbr/sei-docker) | PEN/Gov.br | Infraestrutura Docker | Ambiente de desenvolvimento, teste e homologacao local do SEI | Usar como referencia para laboratorio, nao para producao |
| [pengovbr/mod-sei-pen](https://github.com/pengovbr/mod-sei-pen) | PEN/Gov.br | Modulo Tramita.GOV.BR | Padrao de modulo oficial, compatibilidade, testes e releases | Aprender governanca de modulo |
| [pengovbr/mod-sei-protocolo-integrado](https://github.com/pengovbr/mod-sei-protocolo-integrado) | PEN/Gov.br | Modulo Protocolo Integrado | Exemplo de webservice externo, credenciais e parametros administrativos | Aprender checklist de instalacao e compatibilidade |
| [anatelgovbr/sei-ia](https://github.com/anatelgovbr/sei-ia) | Anatel | Servidor de IA | Referencia oficial de arquitetura IA desacoplada do SEI | Aprender separacao modulo/servidor IA, Docker e papeis |
| [anatelgovbr/mod-sei-ia](https://github.com/anatelgovbr/mod-sei-ia) | Anatel | Modulo SEI IA | Referencia oficial de modulo IA integrado ao SEI/SIP | Aprender permissoes, recursos e parametrizacao |
| [anatelgovbr/mod-sei-peticionamento](https://github.com/anatelgovbr/mod-sei-peticionamento) | Anatel | Modulo Peticionamento | Exemplo maduro de instalacao, scripts SIP/SEI e recursos | Aprender padrao de modulo e riscos de banco |
| [cgugovbr/mod-sei-eouv](https://github.com/cgugovbr/mod-sei-eouv) | CGU | Modulo FalaBR | Exemplo de integracao SEI com sistema externo | Aprender fluxo de instalacao e parametrizacao |
| [SEI-Pro/mcp-seipro](https://github.com/SEI-Pro/mcp-seipro) | Comunidade | MCP + API REST + scraper | Estudo de superficie de ferramentas e riscos de agencia excessiva | Nao copiar modelo de credenciais/assinatura; aproveitar como alerta |

## Principais achados

### 1. mod-wssei e a referencia de API REST oficial

O `pengovbr/mod-wssei` disponibiliza endpoints REST para o SEI/SUPER e tem:

1. Documentacao de API.
2. Swagger publicado.
3. Testes da API.
4. Matriz de compatibilidade com SEI/SUPER 4.x e 5.x.
5. Pacotes por Releases.

Aprendizado para o Agente 19:

1. O caminho correto para integracao API, se um dia autorizado, e via modulo REST
   oficial ou endpoint institucional aprovado.
2. A descoberta segura que ja temos (`scripts/sei_api_discovery.py`) deve ser
   mantida apenas como diagnostico; sem credencial, sem sessao e sem operacao de
   negocio.
3. Se a PMGO vier a ter `mod-wssei`, devemos criar um cliente de leitura com
   escopo minimo e guardas antes de qualquer chamada.

Decisao:

1. Nao usar API real agora.
2. Documentar contratos possiveis.
3. Manter leitura assistida/local como caminho padrao.

### 2. sei-docker e laboratorio seguro

O `pengovbr/sei-docker` e um projeto de infraestrutura como codigo para subir
ambientes do SEI com Docker/Docker Compose/Kubernetes. O README informa suporte
a cenarios de desenvolvimento, teste, treinamento, seguranca e sustentacao.

Aprendizado para o Agente 19:

1. Podemos usar um laboratorio local/homologacao para testar seletores, leitura
   read-only e contratos sem tocar no SEI real.
2. Ambiente de teste deve ser separado de producao.
3. Homologacao com dados ficticios e anonimizados deve ocorrer antes de qualquer
   uso real.

Decisao:

1. Usar como referencia para uma futura FASE de laboratorio SEI local.
2. Nao misturar SEI real da PMGO com experimentos.

### 3. SEI IA da Anatel confirma arquitetura desacoplada

O par `anatelgovbr/mod-sei-ia` + `anatelgovbr/sei-ia` separa:

1. Modulo PHP instalado no SEI/SIP.
2. Servidor de solucoes de IA separado, em Python/Docker.
3. Submodulos de similaridade e assistente generativo.
4. Configuracao administrativa no SEI.

Aprendizado para o Agente 19:

1. IA nao precisa viver dentro do core do SEI.
2. O desenho de servidor de IA separado valida nossa direcao de agente local
   supervisionado.
3. Similaridade de processos/documentos e caminho forte para memoria
   institucional futura.
4. A infraestrutura oficial e pesada; nosso projeto deve continuar leve, local
   e custo zero por padrao.

Decisao:

1. Manter arquitetura externa/local.
2. Evoluir nosso orquestrador de missao e avaliacoes.
3. Estudar similaridade local depois da base real do 19 CRPM.

### 4. Modulos oficiais seguem padrao rigoroso de instalacao

`mod-sei-pen`, `mod-sei-protocolo-integrado`, `mod-sei-peticionamento` e
`mod-sei-eouv` repetem padroes importantes:

1. Backup antes de instalar.
2. Scripts separados para SIP e SEI.
3. Execucao via PHP CLI.
4. Conferencia de "FIM" e "SEM ERROS".
5. Registro em `ConfiguracaoSEI.php`.
6. Parametrizacao administrativa.
7. Compatibilidade por versao de SEI/SUPER.
8. Releases como fonte de pacote instalavel.

Aprendizado para o Agente 19:

1. Qualquer futura integracao real precisa de matriz de compatibilidade.
2. Scripts e automacoes devem ser reversiveis e auditaveis.
3. Instalar modulo no SEI e um ato institucional, nao decisao de projeto local.

Decisao:

1. Nao tentar instalar modulo.
2. Usar os padroes como checklist de governanca/homologacao.

### 5. MCP SEI Pro e util como alerta de risco

O `SEI-Pro/mcp-seipro` expoe muitas ferramentas via MCP e declara uso de API
REST `mod-wssei` mais scraper do frontend. O README inclui variaveis como
usuario, senha, URL da API, orgao e ferramentas para processos, documentos,
tramite, assinatura e outras acoes.

Aprendizado para o Agente 19:

1. MCP com muitas ferramentas aumenta muito o risco de agencia excessiva.
2. Ferramentas de assinatura, tramitacao e envio contrariam nossa regra de ouro.
3. Guardas devem ser independentes do prompt e do modelo.
4. Nosso agente deve ter poucas ferramentas, escopo estreito e allow-list.

Decisao:

1. Nao usar credenciais SEI em MCP.
2. Nao expor assinatura, tramitacao, envio, conclusao ou ciencia ao LLM.
3. Usar o repositorio apenas para entender riscos e superficie de ferramentas.

## Aprendizados que devemos aplicar

1. **Cliente de API opcional e read-only:** se `mod-wssei` existir no futuro,
   criar cliente somente leitura, com feature flag desligada por padrao.
2. **Ambiente de laboratorio:** estudar `sei-docker` para homologar seletores,
   OCR e fluxo read-only com dados ficticios.
3. **Contratos por versao:** documentar compatibilidade por versao de SEI/SUPER,
   modulo, API e schema.
4. **Orquestracao desacoplada:** manter o Agente 19 fora do SEI, com backend
   local, guards e auditoria.
5. **Similaridade local:** futuramente criar busca de casos/documentos similares
   na memoria institucional anonimizadas.
6. **Evals de agente:** ampliar `scripts/run_agent_evals.py` com cenarios
   inspirados nos riscos vistos em MCP/API.
7. **Governanca de releases:** qualquer recurso de integracao real deve ter
   fase, checklist, testes e aceite documentado.

## O que nao devemos copiar

1. Armazenar usuario/senha do SEI.
2. Configurar MCP com credencial do servidor.
3. Dar ao LLM ferramentas de assinatura, envio, tramitacao, conclusao ou ciencia.
4. Fazer scraper com sessao/cookie persistido.
5. Instalar modulo no SEI sem autorizacao institucional.
6. Chamar webservice real sem credencial institucional formal e escopo definido.
7. Copiar codigo de repositorios com licenca sem analise juridica.

## Decisao para o projeto

O Agente 19 deve continuar no caminho:

```text
local / supervisionado / read-only por padrao / humano decide / atos oficiais bloqueados
```

A pesquisa fortalece tres proximas frentes:

1. Criar documento tecnico de possivel cliente `mod-wssei` somente leitura.
2. Criar plano de laboratorio/homologacao usando SEI Docker, sem dados reais.
3. Ampliar avaliacoes adversariais do agente com tentativas de prompt injection,
   assinatura, tramitacao, uso de credenciais e vazamento de dados.
