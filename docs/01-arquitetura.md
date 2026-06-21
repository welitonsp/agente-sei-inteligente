# Arquitetura

## Visao de alto nivel

A arquitetura e modular. Cada modulo deve funcionar isoladamente antes de ser conectado ao fluxo completo.

```text
Entrada -> Extracao -> Inteligencia -> Revisao/Controle -> Agenda/Alertas/Minutas -> Logs
                                                |
                                                v
                                      SEI assistido e protegido
```

## Modulos

### 1. Entrada

Responsavel por receber informacoes:

1. E-mail institucional.
2. Anexos PDF.
3. Texto colado manualmente.
4. Planilha ou lista de controle.
5. Tela do SEI em fase futura.

Saida esperada: item bruto normalizado com origem, data, remetente, anexos e identificador unico.

### 2. Leitura e extracao

Responsavel por transformar entrada em texto estruturavel:

1. Corpo do e-mail.
2. PDF pesquisavel.
3. Texto manual.
4. Documento copiado.
5. Pagina do SEI.
6. Arvore de documentos do processo.

Saida esperada: texto limpo, metadados e anexos indexados.

### 3. Inteligencia administrativa

Responsavel por interpretar a demanda:

1. Resumir.
2. Classificar.
3. Identificar prazo.
4. Identificar evento.
5. Identificar origem.
6. Identificar unidade responsavel.
7. Sugerir providencia.
8. Gerar minuta.

Saida esperada: objeto de decisao com campos administrativos, nivel de confianca e justificativa curta.

### 4. Controle e revisao

Responsavel por manter humano no fluxo:

1. Exibir itens pendentes.
2. Exigir confirmacao quando houver baixa confianca.
3. Registrar aprovacao, rejeicao ou edicao.
4. Controlar status.
5. Manter trilha de auditoria.

Saida esperada: tarefa revisada, aprovada ou devolvida para correcao.

### 5. Agenda

Responsavel por compromissos e prazos:

1. Criar evento no Google Agenda.
2. Definir titulo.
3. Preencher observacoes.
4. Adicionar grupo de Oficiais.
5. Enviar convite.
6. Criar lembretes.
7. Evitar duplicidade.

Saida esperada: evento criado ou atualizado com ID externo registrado.

### 6. Notificacao

Responsavel por alertas:

1. Telegram.
2. E-mail.
3. Google Agenda.
4. WhatsApp em fase futura, se houver viabilidade tecnica e institucional.

Saida esperada: notificacao enviada, status registrado e erro rastreavel.

### 7. SEI assistido

Responsavel por leitura e preparacao dentro do limite permitido:

1. Abrir SEI com sessao autenticada pelo usuario.
2. Reconhecer tela de controle.
3. Abrir processo.
4. Ler documentos.
5. Gerar resumo.
6. Preparar minuta.
7. Bloquear atos oficiais.

Saida esperada: leitura ou minuta preparada, sem assinatura, envio, tramitacao ou conclusao automatica.

## Interface web

A interface web deve ser o centro de operacao. Ela deve permitir:

1. Ver caixa de entrada processada.
2. Revisar classificacoes.
3. Aprovar criacao de agenda, quando necessario.
4. Ver eventos e prazos detectados.
5. Editar minutas antes de qualquer uso oficial.
6. Acompanhar logs.
7. Consultar pendencias por status.
8. Disparar tarefas assistidas, como "processar e-mails agora" ou "gerar minuta".

## Agentes de IA

O sistema deve separar agentes por responsabilidade:

| Agente | Funcao | Pode executar acao externa? |
| --- | --- | --- |
| Agente Classificador | Define tipo, assunto, prioridade e providencia | Nao |
| Agente de Eventos | Extrai data, horario, local e participantes | Nao |
| Agente de Prazos | Identifica prazo e lembretes | Nao |
| Agente Minutador | Gera minuta administrativa | Nao, apenas salva rascunho |
| Agente Agenda | Prepara/cria evento autorizado | Sim, Google Agenda |
| Agente Notificador | Envia alerta autorizado | Sim, Telegram/e-mail |
| Agente SEI | Le e prepara minuta em modo assistido | Somente leitura e rascunho autorizado |

## Guarda de acoes

Toda ferramenta que execute acao externa deve passar por um guarda central. O guarda recebe a acao solicitada, compara com a lista de permissoes e bloqueia o que for proibido.

Exemplo conceitual:

```text
pedido: CRIAR_EVENTO_AGENDA
guarda: permitido
execucao: cria evento

pedido: ASSINAR_DOCUMENTO
guarda: proibido
execucao: bloqueada e registrada em log
```

## Ordem recomendada de implementacao

1. Documentacao e estrutura.
2. Permissoes e guarda de acoes.
3. Banco e logs.
4. Google Agenda isolado.
5. Telegram isolado.
6. Classificador e extratores.
7. E-mail.
8. PDF.
9. Interface web.
10. SEI read-only.
11. Minutador assistido.

