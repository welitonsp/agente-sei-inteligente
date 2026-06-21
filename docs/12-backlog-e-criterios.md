# Backlog e criterios de aceite

## P0 - Fundacao

1. Criar repositorio limpo.
2. Criar estrutura de pastas.
3. Criar documentacao.
4. Criar `.env.example`.
5. Criar `permissions.py`.
6. Criar `sei_action_guard.py`.
7. Criar README.
8. Criar checklist de seguranca.

### Aceite P0

1. Documentacao revisada.
2. Acoes permitidas e proibidas definidas.
3. Estrutura tecnica aprovada.
4. Variaveis sensiveis fora do repositorio.

## P1 - Agenda

1. Criar integracao Google Agenda.
2. Criar evento.
3. Adicionar convidados.
4. Enviar convite.
5. Preencher observacao.
6. Evitar duplicidade.

### Aceite P1 Agenda

1. Evento criado em agenda de teste.
2. Grupo de Oficiais adicionado por configuracao.
3. Observacao segue modelo.
4. Duplicidade bloqueada.
5. Log registrado.

## P1 - Telegram

1. Criar bot.
2. Enviar alerta.
3. Padronizar mensagem.
4. Registrar envio.

### Aceite P1 Telegram

1. Mensagem enviada para chat configurado.
2. Falha registrada quando token/chat estiver incorreto.
3. Alerta nao contem documento completo.

## P1 - Classificacao

1. Criar classificador de documento.
2. Detectar evento.
3. Detectar prazo.
4. Detectar providencia.

### Aceite P1 Classificacao

1. Classificador retorna objeto estruturado.
2. Confianca aparece na resposta.
3. Baixa confianca gera revisao obrigatoria.

## P2 - E-mail

1. Ler e-mails.
2. Processar corpo.
3. Processar anexos.
4. Marcar processado.

### Aceite P2 E-mail

1. E-mail de teste e lido.
2. Anexo e identificado.
3. Mensagem nao e processada duas vezes.
4. Erro de conexao e registrado.

## P2 - PDF

1. Extrair texto.
2. Resumir.
3. Identificar data, horario e local.

### Aceite P2 PDF

1. PDF pesquisavel gera texto.
2. PDF sem texto e marcado como OCR necessario.
3. Dados extraidos aparecem para revisao.

## P3 - SEI

1. Abrir sistema em modo assistido.
2. Ler tela.
3. Ler processo.
4. Ler documento.
5. Gerar minuta.

### Aceite P3 SEI

1. Nenhuma senha do SEI e armazenada.
2. Acoes proibidas sao bloqueadas.
3. Leitura gera log.
4. Minuta e salva como rascunho.
5. Assinatura e envio continuam manuais.

## Criterios de aceite da arquitetura

1. Projeto modular.
2. Acoes proibidas centralizadas.
3. Google Agenda funciona isoladamente.
4. Telegram funciona isoladamente.
5. Classificador funciona sem depender do SEI.
6. SEI entra apenas depois da agenda e alertas.
7. Nao ha senha do SEI no codigo.
8. Ha log de todas as acoes.
9. Ha controle de duplicidade.
10. Agente nunca assina nem envia processo.

