# Estrategia sem modulo oficial SEI IA

## Decisao

Nao ha viabilidade de instalar o modulo oficial SEI IA no ambiente institucional.

Portanto, o projeto nao tentara atuar como modulo interno do SEI. O agente sera externo/local, assistido, seguro e subordinado a sessao individual de cada servidor.

## Objetivo

Manter o agente util para a rotina administrativa sem violar:

1. Identidade individual do servidor.
2. Rastreabilidade do SEI.
3. Responsabilidade por atos oficiais.
4. Sigilo de usuario e senha.
5. Permissoes reais de cada usuario.

## Arquitetura adotada

```text
E-mail/PDF/texto/manual -> Agente -> Agenda/alertas/minutas/logs
                                |
                                v
                    SEI somente por assistencia local read-only
```

## Como o agente trabalha na pratica

### Fluxo 1 - Sem tocar no SEI

1. Servidor encaminha e-mail, PDF ou texto para o agente.
2. Agente extrai conteudo.
3. Agente identifica evento, prazo, origem e providencia.
4. Agente cria agenda e alerta.
5. Agente gera minuta fora do SEI.
6. Servidor revisa e pratica o ato oficial manualmente no SEI.

Este sera o fluxo principal do MVP.

### Fluxo 2 - Assistente local de leitura

1. Servidor acessa o SEI manualmente na propria estacao.
2. Servidor digita usuario e senha manualmente.
3. Servidor abre processo ou documento.
4. Servidor aciona o agente local com comando explicito, como `Ler pagina atual`.
5. Agente extrai apenas texto visivel/autorizado.
6. Agente resume, classifica e sugere providencia.
7. Agente para.
8. Servidor decide e executa manualmente qualquer ato oficial.

## Formas tecnicas possiveis

### Opcao 1 - Copiar e colar controlado

O servidor copia o texto do SEI e cola no painel do agente.

Vantagens:

1. Simples.
2. Seguro.
3. Sem automacao no SEI.
4. Preserva totalmente a autoria.

Desvantagem:

1. Exige acao manual.

### Opcao 2 - Upload de PDF baixado pelo servidor

O servidor gera/baixa PDF autorizado e envia ao agente.

Vantagens:

1. Bom para processos/documentos longos.
2. Facil de auditar.
3. Nao exige senha no agente.

Desvantagem:

1. Depende de rotina correta de armazenamento e descarte.

### Opcao 3 - Extensao de navegador read-only

Uma extensao local le somente o conteudo da aba atual do SEI quando o servidor clica em um botao.

Vantagens:

1. Melhor experiencia de uso.
2. Nao precisa instalar modulo no SEI.
3. Usa a sessao real do servidor.

Riscos:

1. Exige autorizacao institucional.
2. Precisa auditoria.
3. Precisa bloquear botoes e acoes oficiais.

Essa e a forma mais proxima do "robozinho na tela do SEI". Como nao podemos instalar modulo oficial no servidor SEI, o robozinho deve morar na estacao do servidor ou no navegador, nao dentro do codigo do SEI.

Comportamento esperado:

1. Exibir icone flutuante apenas quando a URL for do SEI autorizado.
2. Abrir painel lateral ao clique.
3. Permitir informar numero de processo para identificacao/conferencia.
4. Ler a pagina atual ou documentos acessiveis ja abertos pelo servidor.
5. Enviar texto extraido para o backend local do agente.
6. Receber resumo, prazo, finalidade, unidade sugerida e minuta.
7. Nunca clicar em botoes sensiveis.

Regra: no MVP, informar o numero do processo nao autoriza o agente a pesquisar ou navegar no SEI. O servidor deve abrir o processo manualmente, colar o texto ou enviar PDF baixado por ele. Navegacao automatica, ainda que somente para busca, fica fora do MVP e depende de autorizacao especifica.

### Opcao 4 - Automacao local read-only com Playwright

O agente abre ou conecta a um navegador local usado pelo servidor e executa apenas leitura.

Vantagens:

1. Pode ler estrutura da pagina.
2. Pode ajudar em processos longos.

Riscos:

1. Mais sensivel que copiar/colar.
2. Deve ser proibido de clicar em botoes oficiais.
3. Deve parar em tela inesperada.

## Proibicoes tecnicas

O agente nao pode:

1. Digitar usuario.
2. Digitar senha.
3. Guardar cookies do SEI.
4. Guardar token de sessao.
5. Compartilhar sessao entre servidores.
6. Fazer login automatico.
7. Rodar com conta unica.
8. Assinar documento.
9. Enviar processo.
10. Tramitar processo.
11. Concluir processo.
12. Dar ciencia.
13. Excluir ou cancelar documento.
14. Liberar acesso externo.
15. Alterar sigilo ou credencial.

## Design recomendado para MVP

Criar primeiro:

1. Painel web local.
2. Entrada por e-mail.
3. Upload de PDF.
4. Campo `colar texto do SEI`.
5. Classificador de prazo/evento.
6. Gerador de minuta fora do SEI.
7. Google Agenda.
8. Telegram.
9. Log.
10. Prototipo do robozinho em modo simulado no painel web.

Deixar para depois:

1. Leitura direta da pagina do SEI.
2. Extensao de navegador.
3. Automacao local read-only.
4. Busca/navegacao automatica por numero de processo.

Quando evoluir para o robozinho real:

1. Comecar com extensao read-only.
2. Ativar apenas para usuarios autorizados.
3. Mostrar aviso de que a sessao e do servidor.
4. Registrar todas as analises solicitadas.
5. Bloquear qualquer acao de escrita no SEI.

Nao fazer:

1. Escrita no SEI.
2. Login automatico.
3. Conta compartilhada.
4. WebService para praticar ato oficial.

## Regra de interface

Na tela do agente deve haver separacao clara:

```text
Assistente Administrativo
- Processar e-mail
- Importar PDF
- Colar texto
- Gerar resumo
- Gerar minuta
- Criar agenda
- Enviar alerta

SEI
- Sem login automatico
- Sem senha armazenada
- Atos oficiais somente no SEI pelo servidor
```

## Conclusao

Sem modulo oficial, o projeto continua viavel. A estrategia muda de "IA integrada ao SEI" para "assistente administrativo externo/local". Isso e mais simples, mais barato e mais seguro para iniciar.

O agente deve acelerar leitura, organizacao, agenda, alertas e minutas. A responsabilidade dos atos oficiais continua com cada servidor, usando seu proprio usuario e senha no SEI.
