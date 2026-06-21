# Manual operacional

## Rotina diaria recomendada

1. Abrir o painel web do agente.
2. Conferir a fila de entradas.
3. Processar novos e-mails e anexos.
4. Revisar eventos e prazos detectados.
5. Confirmar ou corrigir dados de agenda.
6. Verificar alertas enviados.
7. Revisar minutas geradas.
8. Encaminhar ao responsavel humano para assinatura ou providencia oficial.

## Estados de uma demanda

| Estado | Significado |
| --- | --- |
| Recebida | Entrada cadastrada, ainda nao analisada |
| Extraida | Texto e metadados extraidos |
| Classificada | IA identificou tipo, assunto e providencia |
| Pendente de revisao | Precisa de validacao humana |
| Agendada | Evento ou prazo criado na agenda |
| Alertada | Notificacao enviada |
| Minuta gerada | Rascunho criado para revisao |
| Concluida | Fluxo administrativo de apoio encerrado |
| Bloqueada | Acao proibida ou inconsistente detectada |
| Erro | Falha tecnica a tratar |

## Processar e-mail com evento

1. O agente le o e-mail.
2. Extrai corpo e anexos.
3. Classifica como evento, curso, reuniao, solenidade ou convocacao.
4. Extrai titulo, data, horario e local.
5. Gera resumo.
6. Verifica duplicidade.
7. Cria evento no Google Agenda.
8. Adiciona grupo de Oficiais.
9. Envia convite.
10. Envia alerta no Telegram.
11. Registra log.
12. Marca e-mail como processado.

## Processar documento com prazo

1. O agente extrai o texto do documento.
2. Identifica prazo, origem, assunto e responsavel.
3. Cria evento de prazo na agenda.
4. Configura lembretes.
5. Envia alerta ao responsavel ou grupo.
6. Registra pendencia no painel.

## Gerar minuta

1. Usuario seleciona demanda.
2. Agente resume o contexto.
3. Usuario escolhe tipo de minuta.
4. Agente gera rascunho.
5. Usuario revisa e edita.
6. Sistema salva minuta como rascunho.
7. Ato oficial continua manual.

## Operar SEI assistido

1. Usuario acessa o SEI manualmente.
2. Agente usa a sessao ja autenticada, sem guardar senha.
3. Agente le processo ou documento autorizado.
4. Agente resume e sugere providencia.
5. Agente pode preparar minuta, se habilitado.
6. Agente para antes de qualquer assinatura, envio, tramitacao, conclusao ou ciencia.

## Erros comuns

| Erro | Tratamento |
| --- | --- |
| Data ambigua | Enviar para revisao humana |
| Horario ausente | Criar pendencia, nao criar evento automatico sem regra definida |
| PDF sem texto | Marcar como OCR necessario |
| Evento duplicado | Nao criar novo evento; vincular ao registro existente |
| Token expirado | Solicitar nova autenticacao |
| Acao SEI proibida | Bloquear, registrar log e avisar usuario |

## Boas praticas

1. Revisar eventos antes do envio automatico enquanto o sistema estiver em homologacao.
2. Usar documentos reais somente em ambiente autorizado.
3. Criar base de modelos oficiais aprovados.
4. Manter lista de Oficiais atualizada no Google Groups ou configuracao equivalente.
5. Revisar logs semanalmente.

