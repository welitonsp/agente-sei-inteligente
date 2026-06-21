# Plano de testes

## Objetivo

Garantir que os modulos funcionem isoladamente e que o fluxo completo seja seguro, auditavel e util para a rotina administrativa.

## Piramide de testes

1. Testes unitarios para regras, extratores e permissoes.
2. Testes de integracao para agenda, Telegram, e-mail e banco.
3. Testes end-to-end para o fluxo web.
4. Testes manuais supervisionados para SEI assistido.

## Testes obrigatorios de seguranca

1. `ASSINAR_DOCUMENTO` deve ser bloqueado.
2. `ENVIAR_PROCESSO` deve ser bloqueado.
3. `TRAMITAR_PROCESSO` deve ser bloqueado.
4. `CONCLUIR_PROCESSO` deve ser bloqueado.
5. `EXCLUIR_DOCUMENTO` deve ser bloqueado.
6. Toda acao bloqueada deve gerar log.
7. Nenhuma senha do SEI deve aparecer em arquivo versionado.

## Testes do classificador

Casos minimos:

1. E-mail de evento com data, horario e local claros.
2. E-mail de evento sem horario.
3. Documento com prazo explicito.
4. Documento informativo sem providencia.
5. Documento com mais de uma data.
6. Texto curto e incompleto.

## Testes de agenda

1. Criar evento valido.
2. Adicionar grupo de Oficiais.
3. Preencher observacao padronizada.
4. Criar lembretes.
5. Bloquear duplicidade.
6. Registrar erro de autenticacao.
7. Registrar ID do evento externo.

## Testes de Telegram

1. Enviar alerta informativo.
2. Enviar alerta urgente.
3. Simular token invalido.
4. Evitar envio duplicado.
5. Confirmar que mensagem nao contem documento completo.

## Testes de e-mail

1. Ler e-mail de teste.
2. Ignorar e-mail ja processado.
3. Detectar anexo.
4. Tratar falha de conexao.
5. Registrar status processado.

## Testes de PDF

1. Extrair texto de PDF pesquisavel.
2. Marcar PDF sem texto como OCR necessario.
3. Detectar data, horario e local.
4. Gerar resumo.
5. Registrar hash do documento.

## Testes da interface web

1. Listar demandas.
2. Abrir demanda.
3. Corrigir classificacao.
4. Aprovar evento.
5. Gerar minuta.
6. Consultar logs.
7. Exibir erro e bloqueio.
8. Funcionar em tela de celular para operacoes basicas.

## Testes do SEI assistido

Esses testes devem ser feitos somente quando a etapa SEI for autorizada.

1. Abrir SEI com autenticacao humana.
2. Ler processo autorizado ja aberto pelo servidor.
3. Ler documento ja aberto ou texto/PDF fornecido.
4. Gerar resumo.
5. Bloquear botao de assinatura.
6. Bloquear envio/tramitacao.
7. Parar em tela desconhecida.
8. Registrar log sem armazenar senha.
9. Nao pesquisar processo por numero no MVP.
10. Nao armazenar cookie/token/sessao.

## Testes do robozinho

1. Analisar texto colado com numero de processo informado.
2. Analisar PDF baixado pelo servidor.
3. Conferir divergencia entre numero informado e numero encontrado no texto.
4. Inventariar processo com muitos documentos.
5. Priorizar despachos, oficios, documentos recentes e documentos com prazo.
6. Marcar PDF sem texto como `ocr_necessario`.
7. Marcar documento inacessivel como `inacessivel`.
8. Impedir conclusao "sem prazo" quando houver documento relevante nao lido.
9. Exigir revisao humana quando a unidade do 19 CRPM nao puder ser definida.
10. Bloquear qualquer tentativa de acao oficial.

## Massa de teste

Usar exemplos anonimizados:

1. E-mails de convocacao.
2. Oficios de prazo.
3. Convites de reuniao.
4. PDFs pesquisaveis.
5. PDFs ruins.
6. Minutas aprovadas como modelo.

## Aceite da homologacao

O MVP so deve entrar em rotina real quando:

1. Agenda funcionar isoladamente.
2. Telegram funcionar isoladamente.
3. Duplicidade estiver testada.
4. Acoes proibidas estiverem testadas.
5. Logs estiverem consultaveis.
6. Operador souber revisar baixa confianca.
