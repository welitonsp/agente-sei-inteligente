# Agente 19 - Assistente visual flutuante do 19 CRPM

## Visao do gestor de processos

O objetivo e criar um assistente visual (o Agente 19, Funcionario Digital de IA) que apareca na tela do SEI como uma janela ou logo flutuante. O servidor, ja logado exclusivamente na pagina oficial do SEI com seu proprio usuario e senha, clica no Agente 19, informa o numero do processo SEI e aciona o assistente.

O agente deve:

1. Analisar o processo informado ou aberto pelo servidor.
2. Ler os documentos acessiveis naquela sessao.
3. Procurar somente o que interessa ao 19 CRPM.
4. Ignorar ou separar documentos de outras unidades militares quando nao tiverem relacao com o 19 CRPM.
5. Explicar o conteudo em linguagem clara.
6. Identificar se ha prazo.
7. Identificar finalidade.
8. Identificar unidade de origem.
9. Sugerir qual unidade pertencente ao 19 CRPM deve receber a providencia.
10. Exportar o processo em PDF e analisar sua totalidade.
11. Perguntar se o usuario deseja criar Oficio, Despacho, Ordem de Atendimento, etc.
12. Apos confirmacao, criar a minuta dentro do SEI, preencher, e avisar que esta pronta para revisao humana.
13. O humano revisa, corrige, assina e tramita manualmente.
14. Registrar log da analise.

## Restricao tecnica

Como nao e possivel instalar o modulo oficial SEI IA, o robozinho nao sera um modulo interno do SEI.

As alternativas seguras sao:

1. Extensao de navegador read-only.
2. Painel lateral local.
3. Aplicacao desktop com janela flutuante.
4. Prototipo no painel web com copia/cola ou upload de PDF.

## Regra de identidade

O robozinho nao faz login. O servidor faz login manualmente no SEI.

O processo deve ser pelo usuario individual do servidor. Cada servidor usa seu proprio usuario e sua propria senha. O robozinho so atua depois que o servidor ja autenticou a sessao.

O robozinho nao pode:

1. Guardar usuario.
2. Guardar senha.
3. Usar conta unica.
4. Compartilhar sessao.
5. Agir em nome de servidor diferente.
6. Praticar ato oficial.

## Modos de uso

### Modo MVP - seguro

No MVP, o servidor deve abrir o processo/documento no SEI ou fornecer texto/PDF ao agente.

O numero do processo serve para:

1. Identificar a demanda.
2. Conferir se o texto/PDF corresponde ao processo correto.
3. Registrar log interno do agente.

O numero do processo nao autoriza o agente a pesquisar, navegar ou clicar sozinho no SEI.

### Modo futuro - leitura assistida da pagina

Depois de autorizado, uma extensao read-only podera ler a pagina atual do SEI. Mesmo nesse modo, o servidor continua responsavel por abrir o processo e acionar o robozinho.

### Fora do escopo

1. Busca automatica por numero de processo.
2. Login automatico.
3. Navegacao automatica por menus do SEI.
4. Clique em botoes de ato oficial.

## Fluxo principal

```text
Servidor abre SEI
        |
        v
Servidor faz login com usuario/senha proprios
        |
        v
Servidor digita a senha manualmente
        |
        v
Servidor clica no robozinho
        |
        v
Painel abre
        |
        v
Servidor informa numero do processo
        |
        v
Servidor abre o processo/documento ou fornece texto/PDF
        |
        v
Agente le apenas o conteudo fornecido ou visivel
        |
        v
Agente filtra interesse do 19 CRPM
        |
        v
Agente explica conteudo, prazo, finalidade e unidade sugerida
        |
        v
Agente gera minuta/arquivo fora do SEI
        |
        v
Servidor revisa e pratica ato oficial manualmente
```

## Leitura dos documentos

O agente deve trabalhar por etapas:

1. Ler arvore/lista de documentos do processo.
2. Identificar tipo de cada documento.
3. Ler metadados disponiveis: numero, tipo, data, unidade, interessado e assunto.
4. Priorizar documentos recentes, despachos, oficios, convocacoes, anexos e documentos com prazo.
5. Extrair texto.
6. Montar resumo por documento.
7. Montar resumo consolidado do processo.
8. Apontar documentos que embasam a conclusao.

## Leitura de processos grandes

Quando houver muitos documentos, o agente deve usar uma fila de leitura:

1. Inventariar documentos primeiro, sem resumir tudo de uma vez.
2. Priorizar documentos recentes, despachos, oficios, documentos com prazo e documentos vindos de Alto Comando.
3. Marcar anexos grandes como `leitura_pendente` quando excederem limite configurado.
4. Marcar PDF sem texto como `ocr_necessario`.
5. Registrar documentos inacessiveis como `nao_lido`.
6. Nunca concluir que nao ha prazo se algum documento relevante ficou sem leitura.
7. Apresentar lista de documentos usados como fonte.

Estados de leitura:

```text
lido
parcial
nao_lido
ocr_necessario
inacessivel
ignorado_por_regra
```

## Filtro de interesse do 19 CRPM

O agente deve separar:

1. Documentos diretamente ligados ao 19 CRPM.
2. Documentos de Alto Comando que demandam providencia do 19 CRPM.
3. Documentos de outras unidades militares sem providencia para o 19 CRPM.
4. Documentos informativos.
5. Documentos com prazo.
6. Documentos com evento.
7. Documentos que exigem minuta.

## Base de regras necessaria

Para funcionar bem, o agente precisa de tabelas internas.

### Unidades do 19 CRPM

Exemplo de estrutura:

```text
sigla:
nome:
tipo:
cidade:
responsavel:
assuntos_atendidos:
palavras_chave:
```

### Unidades de Alto Comando relevantes

Exemplo de estrutura:

```text
sigla:
nome:
tipo:
peso_prioridade:
assuntos_geralmente_relevantes:
```

### Regras de direcionamento

Exemplo:

```text
Se assunto contem "evento operacional" e local pertence a area X -> sugerir unidade Y.
Se documento veio do Alto Comando e menciona 19 CRPM -> classificar como alta prioridade.
Se ha prazo inferior a 3 dias -> alerta urgente.
Se documento e apenas informativo e nao menciona area do 19 CRPM -> arquivar como nao relevante.
```

## Saida esperada da analise

```json
{
  "processo_sei": "",
  "assunto": "",
  "finalidade": "",
  "resumo_executivo": "",
  "ha_prazo": true,
  "prazo": "",
  "tipo_prazo": "",
  "unidade_origem": "",
  "interesse_19crpm": "direto",
  "unidade_19crpm_sugerida": "",
  "justificativa": "",
  "providencia_sugerida": "",
  "documentos_relevantes": [],
  "documentos_ignorados": [],
  "agenda_sugerida": null,
  "minuta_sugerida": "",
  "confianca": 0.0,
  "revisao_humana_obrigatoria": true
}
```

## Exemplos de perguntas que o robozinho deve responder

1. Este processo interessa ao 19 CRPM?
2. Qual e o assunto principal?
3. Existe prazo?
4. Qual documento cria a demanda?
5. Qual documento e apenas anexo?
6. Qual unidade originou a demanda?
7. Qual unidade do 19 CRPM deve responder?
8. Precisa criar evento na agenda?
9. Precisa alertar Oficiais?
10. Qual minuta devo preparar?

## Acoes permitidas

1. Ler texto visivel/autorizado.
2. Resumir.
3. Classificar.
4. Identificar prazo.
5. Identificar evento.
6. Sugerir unidade responsavel.
7. Criar evento no Google Agenda.
8. Enviar alerta externo.
9. Gerar minuta fora do SEI.
10. Registrar log.

## Acoes proibidas

1. Assinar documento.
2. Enviar processo.
3. Tramitar processo.
4. Concluir processo.
5. Dar ciencia.
6. Excluir documento.
7. Cancelar documento.
8. Alterar nivel de acesso.
9. Conceder credencial.
10. Liberar acesso externo.
11. Inserir documento diretamente no SEI sem revisao humana e autorizacao institucional.

## MVP recomendado

Antes de criar extensao real, construir um prototipo no painel web:

1. Campo `Numero do processo SEI`.
2. Campo `Texto copiado do SEI`.
3. Upload de PDFs baixados pelo servidor.
4. Botao `Analisar para o 19 CRPM`.
5. Resultado estruturado.
6. Botao `Gerar minuta`.
7. Botao `Criar agenda`.
8. Botao `Enviar alerta`.

Depois, evoluir para:

1. Extensao de navegador read-only.
2. Botao flutuante.
3. Painel lateral.
4. Leitura automatica da pagina atual.
5. Analise de documentos do processo.

Busca automatica por numero de processo deve continuar fora do MVP. Se algum dia for autorizada, devera ser tratada como funcionalidade separada, com testes proprios e sem qualquer permissao de ato oficial.

## Decisoes pendentes

1. Lista oficial de unidades do 19 CRPM.
2. Lista oficial de unidades de Alto Comando relevantes.
3. Regras de direcionamento por assunto.
4. Definicao do que significa "criar o arquivo".
5. Autorizacao para extensao de navegador.
6. Politica para armazenar ou descartar textos extraidos do SEI.
