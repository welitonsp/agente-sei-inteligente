# Interface web

## Objetivo

A pagina web deve ser o painel de comando do agente. Ela nao deve ser apenas uma tela demonstrativa; deve permitir operar a rotina administrativa.

## Usuarios da interface

1. Administrador do sistema.
2. Operador administrativo.
3. Revisor/aprovador.
4. Leitor de acompanhamento.

## Tela inicial

A primeira tela deve mostrar trabalho real:

1. Demandas novas.
2. Pendencias de revisao.
3. Prazos proximos.
4. Eventos criados.
5. Minutas aguardando revisao.
6. Alertas com falha.

## Areas principais

### Robozinho SEI

O robozinho SEI e a interface de assistencia rapida para o servidor logado no SEI. Como nao havera modulo oficial instalado, ele deve ser pensado como extensao de navegador, painel lateral local ou janela flutuante da aplicacao.

Fluxo esperado:

1. Servidor acessa o SEI com usuario e senha proprios.
2. Servidor clica no robozinho.
3. Robo abre painel lateral.
4. Servidor informa numero do processo SEI ou pede leitura da pagina atual.
5. Agente le somente documentos acessiveis naquela sessao.
6. Agente filtra o que interessa ao 19 CRPM.
7. Agente explica assunto, finalidade, prazo e providencia sugerida.
8. Agente indica unidade do 19 CRPM para direcionamento.
9. Agente gera minuta/arquivo fora do SEI para revisao.

Comandos visiveis:

1. `Analisar processo`.
2. `Ler pagina atual`.
3. `Identificar prazos`.
4. `Filtrar 19 CRPM`.
5. `Sugerir unidade responsavel`.
6. `Gerar minuta`.
7. `Criar evento na agenda`.
8. `Enviar alerta`.

Comandos proibidos:

1. `Assinar`.
2. `Enviar processo`.
3. `Tramitar`.
4. `Concluir`.
5. `Dar ciencia`.
6. `Excluir`.
7. `Cancelar`.
8. `Alterar sigilo`.

### Caixa de entrada

Lista de e-mails, PDFs e textos manuais processados.

Campos:

1. Origem.
2. Remetente.
3. Assunto.
4. Data de recebimento.
5. Tipo detectado.
6. Status.
7. Confianca da IA.

### Revisao administrativa

Tela para validar a interpretacao da IA.

Controles:

1. Editar titulo.
2. Corrigir data e horario.
3. Corrigir local.
4. Definir responsavel.
5. Aprovar agenda.
6. Solicitar nova analise.
7. Bloquear demanda.

### Agenda

Visualizacao dos eventos e prazos criados.

Deve permitir:

1. Ver evento vinculado a demanda.
2. Ver convidados.
3. Ver lembretes.
4. Ver chave de duplicidade.
5. Abrir link externo do Google Agenda.

### Minutas

Editor de rascunhos administrativos.

Deve permitir:

1. Escolher modelo.
2. Gerar minuta.
3. Editar texto.
4. Salvar rascunho.
5. Exportar ou copiar texto.
6. Registrar aprovacao humana.

### SEI assistido

Area futura para apoio ao SEI.

Deve exibir:

1. Processo selecionado.
2. Documentos lidos.
3. Resumo.
4. Providencia sugerida.
5. Minuta gerada.
6. Alertas de acao proibida.

### Auditoria

Lista de acoes executadas e bloqueadas.

Campos:

1. Data e hora.
2. Usuario.
3. Acao.
4. Origem.
5. Resultado.
6. Motivo.

## Estados visuais

| Estado | Tratamento |
| --- | --- |
| Novo | Destacar como pendente |
| Alta confianca | Permitir fluxo rapido |
| Baixa confianca | Exigir revisao |
| Erro | Exibir causa e tentativa de reprocessamento |
| Bloqueado | Mostrar regra violada |
| Concluido | Manter consultavel |

## Acoes de pagina web

A interface pode disparar tarefas como:

1. Processar e-mails agora.
2. Importar PDF.
3. Colar texto manual.
4. Gerar resumo.
5. Criar evento.
6. Enviar alerta.
7. Gerar minuta.
8. Reprocessar item.

A interface nao deve oferecer botao para atos oficiais proibidos no SEI.

## Requisitos de seguranca da interface

1. Autenticacao obrigatoria em ambiente real.
2. Perfis de acesso.
3. Sessao com timeout.
4. Logs de acoes do usuario.
5. Protecao contra exposicao de tokens.
6. Aviso claro quando item depender de revisao humana.

## MVP visual recomendado

Para o MVP, uma interface simples e funcional e melhor do que uma tela bonita sem operacao. A prioridade deve ser:

1. Tabela de demandas.
2. Painel de revisao.
3. Formulario de evento.
4. Editor de minuta.
5. Log de auditoria.
