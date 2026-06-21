# Visao geral

## Produto

O Agente SEI Inteligente - 19 CRPM e uma plataforma web de apoio administrativo. Ele recebe demandas por e-mail, PDF, texto manual e futuramente por leitura assistida do SEI, entende o conteudo, organiza providencias, cria agenda, envia alertas, gera minutas e registra historico.

O produto nao e um robo autonomo para praticar atos oficiais. Ele e um agente assistivo: prepara o trabalho e deixa a decisao final com o usuario humano.

## Problema

A rotina administrativa exige acompanhamento constante de documentos, processos, prazos, convites, eventos, despachos, oficios, respostas e providencias. O risco operacional aparece quando uma demanda importante fica perdida em e-mail, PDF, processo, grupo de mensagens ou memoria individual.

O problema central nao e apenas resumir texto. O problema e converter informacao administrativa em acao controlada:

1. Identificar o que chegou.
2. Entender assunto, origem e urgencia.
3. Detectar prazo ou evento.
4. Criar agenda e lembretes.
5. Avisar os Oficiais.
6. Gerar minuta.
7. Registrar pendencia.
8. Manter humano no controle do ato oficial.

## Usuarios

| Usuario | Necessidade |
| --- | --- |
| Comando / chefia | Visao rapida de demandas, prazos, eventos e pendencias |
| Oficiais | Receber convites, alertas e resumos objetivos |
| Secretaria / administracao | Processar e acompanhar documentos com menor retrabalho |
| Usuario aprovador | Revisar minutas e praticar atos oficiais manualmente |

## Canais

| Canal | Uso |
| --- | --- |
| Interface web | Painel principal, revisao, controle e aprovacao |
| Celular | Alertas, convites e acompanhamento rapido |
| Google Agenda | Eventos, prazos e lembretes |
| Telegram | Alertas operacionais no MVP |
| E-mail institucional | Entrada de demandas e notificacoes |
| SEI | Sistema oficial, integrado somente em modo assistido |

## Escopo funcional

Dentro do escopo:

1. Leitura de e-mail e anexos.
2. Extracao de texto de PDF pesquisavel.
3. Classificacao administrativa.
4. Identificacao de evento e prazo.
5. Criacao de evento no Google Agenda.
6. Envio de convite para grupo de Oficiais.
7. Alertas no celular.
8. Geracao de minutas.
9. Dashboard de pendencias.
10. Logs, auditoria e controle de duplicidade.

Fora do escopo da automacao:

1. Assinar documentos no SEI.
2. Enviar ou tramitar processos.
3. Concluir processos.
4. Excluir, cancelar ou alterar documentos oficiais.
5. Dar ciencia automaticamente.
6. Alterar sigilo automaticamente.
7. Liberar acesso externo ou conceder credenciais.

## Resultado esperado

O sistema deve reduzir perda de prazo, padronizar a triagem administrativa e centralizar a memoria operacional da unidade, sem enfraquecer controle humano, seguranca institucional ou conformidade com o SEI.

