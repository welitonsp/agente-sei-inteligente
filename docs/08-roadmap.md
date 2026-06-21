# Roadmap

## Etapa 1 - Fundacao documental

Resultado:

1. README.
2. Documentacao de arquitetura.
3. Regras de seguranca.
4. Manual operacional.
5. Backlog.
6. Perguntas pendentes.
7. `.env.example`.

Status: iniciado.

## Etapa 2 - Fundacao tecnica

Resultado:

1. Estrutura de pastas.
2. Configuracao local.
3. Banco SQLite.
4. Logger.
5. Auditoria.
6. Permissoes.
7. Guarda de acoes.
8. Testes de permissoes.

## Etapa 3 - MVP Google Agenda

Resultado:

1. Autenticacao Google.
2. Criacao de evento.
3. Adicao do grupo de Oficiais.
4. Observacao padronizada.
5. Lembretes.
6. Duplicidade.
7. Testes isolados.

## Etapa 4 - MVP celular

Resultado:

1. Bot Telegram.
2. Mensagens padronizadas.
3. Status de envio.
4. Reenvio em falha.
5. Logs de notificacao.

## Etapa 5 - Leitura de e-mail

Resultado:

1. Conexao com e-mail institucional.
2. Leitura de caixa de entrada.
3. Extracao de corpo e anexos.
4. Marcacao como processado.
5. Evitar reprocessamento.

## Etapa 6 - Leitura de PDF

Resultado:

1. Extracao de texto.
2. Identificacao de PDF sem texto.
3. Resumo.
4. Extracao de data, horario e local.
5. Registro do documento.

## Etapa 7 - Inteligencia administrativa

Resultado:

1. Classificador.
2. Extrator de eventos.
3. Extrator de prazos.
4. Sugeridor de providencia.
5. Gerador de minuta.
6. Indicador de confianca.

## Etapa 8 - Interface web

Resultado:

1. Painel de demandas.
2. Fila de revisao.
3. Visualizacao de agenda.
4. Editor de minuta.
5. Logs.
6. Configuracoes.

## Etapa 9 - SEI read-only

Resultado:

1. Abertura manual do SEI pelo servidor.
2. Uso da sessao ja autenticada na estacao do servidor.
3. Leitura assistida somente da pagina atual ou documento selecionado.
4. Resumo.
5. Sem senha armazenada.
6. Sem usuario unico.
7. Sem atos oficiais.

## Etapa 10 - Minutador SEI assistido

Resultado:

1. Gerar minuta fora do SEI.
2. Exibir texto para revisao humana.
3. Permitir copia manual pelo servidor.
4. Bloquear assinatura e envio.
5. Registrar auditoria interna do agente.

Observacao: como nao ha modulo oficial SEI IA disponivel para instalacao, nao sera prevista escrita automatica dentro do SEI na versao 1.

## Etapa 11 - Operacao v1

Resultado:

1. Agente funcional em rotina real controlada.
2. Agenda.
3. Celular.
4. E-mail.
5. PDF.
6. Minutas.
7. Logs.
8. Seguranca.
