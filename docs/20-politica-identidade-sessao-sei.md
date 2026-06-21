# Politica de identidade, sessao e rastreabilidade no SEI

## Regra central

O agente nao pode usar um unico usuario e senha para operar o SEI em nome de varios servidores.

Cada servidor publico deve acessar o SEI com sua propria credencial, na sua propria sessao, assumindo a responsabilidade pelos atos praticados.

Regra operacional ajustada: o acesso deve ser feito pelo usuario individual do servidor. O agente pode aguardar a sessao autenticada e reconhecer que ha uma sessao ativa, mas nao deve armazenar, repetir, compartilhar ou digitar automaticamente a senha do servidor.

## Motivo

O SEI registra historico e rastreabilidade das operacoes. O historico do processo pode mostrar data, unidade, usuario e descricao das operacoes realizadas. Alem disso, normas de uso de SEI reforcam que login, senha e assinatura sao pessoais e intransferiveis.

Logo, se um agente central usar uma credencial unica, o sistema registrara as acoes como se fossem daquele usuario unico, mesmo quando a demanda veio de outro servidor. Isso e tecnicamente errado e administrativamente arriscado.

## Politicas obrigatorias

1. Nao armazenar senha do SEI.
2. Nao compartilhar usuario do SEI.
3. Nao usar conta generica para atos oficiais.
4. Nao executar automacao em segundo plano no SEI.
5. Nao praticar ato oficial sem usuario humano autenticado.
6. Nao mascarar autoria de acesso, edicao, ciencia, envio, conclusao ou assinatura.
7. Nao permitir que um servidor opere processo em nome de outro pela interface do agente.

## Modelo correto de sessao

```text
Servidor senta na propria estacao
        |
        v
Servidor abre navegador e acessa SEI com usuario/senha propria
        |
        v
Servidor digita a senha manualmente
        |
        v
Agente local identifica apenas a sessao ativa daquele servidor
        |
        v
Agente le, resume, sugere e prepara
        |
        v
Servidor decide e pratica ato oficial manualmente
```

## Como o agente deve trabalhar

### Permitido

1. Ler documento visivel ao servidor autenticado.
2. Resumir processo/documento.
3. Identificar prazo.
4. Identificar evento.
5. Criar agenda externa.
6. Enviar alerta.
7. Gerar minuta fora do SEI.
8. Preparar texto para revisao.
9. Registrar log interno do agente.

### Proibido

1. Digitar usuario e senha do servidor.
2. Guardar senha.
3. Reutilizar sessao de outro servidor.
4. Assinar documento.
5. Enviar processo.
6. Tramitar processo.
7. Concluir processo.
8. Dar ciencia automatica.
9. Excluir ou cancelar documento.
10. Alterar sigilo ou credencial.

## Opcoes de arquitetura

### Opcao A - Assistente externo sem acesso ao SEI

O agente trabalha com e-mail, PDF, agenda, Telegram e minutas. O SEI continua manual.

Vantagens:

1. Menor risco.
2. Nao exige credenciais SEI.
3. Preserva totalmente a autoria dos atos.
4. Bom para MVP.

Limite:

1. Nao le diretamente processos dentro do SEI.

### Opcao B - Assistente local por estacao

O agente roda na estacao de trabalho do servidor ou no navegador dele. Ele so usa a sessao que o servidor abriu manualmente.

Vantagens:

1. Mantem identidade individual.
2. Respeita permissao real do usuario.
3. Ajuda o servidor sem virar usuario generico.

Riscos:

1. Precisa de controle forte para nao clicar em atos oficiais.
2. Precisa bloquear seletores sensiveis.
3. Precisa de logs locais.

### Opcao C - Modulo institucional dentro do SEI

Uso de modulo oficial como SEI IA, instalado e configurado pelo administrador do SEI.

Vantagens:

1. Melhor integracao com perfis.
2. Melhor respeito a permissoes internas.
3. Caminho institucional.

Limites:

1. Depende do orgao gestor do SEI.
2. Exige infraestrutura.
3. Exige instalacao no ambiente oficial.

Status atual: indisponivel para o projeto.

### Opcao D - WebService central

Um sistema externo chama WebServices do SEI.

Para o nosso caso, esta opcao deve ser limitada a consultas autorizadas. Nao deve ser usada para atos oficiais em nome de usuarios individuais, pois tende a operar como sistema integrado e nao como a sessao pessoal do servidor na estacao.

WebServices de escrita devem permanecer bloqueados ate autorizacao formal especifica do orgao gestor do SEI e revisao juridica/administrativa. A existencia tecnica da operacao no manual nao autoriza implementacao no agente.

## Recomendacao para o 19 CRPM

Fase 1:

1. Sem login no SEI.
2. Processar e-mail, PDF e texto manual.
3. Criar agenda e alertas.
4. Gerar minutas para revisao.

Fase 2:

1. Leitura assistida do SEI na propria estacao do servidor.
2. Usuario faz login manual.
3. Agente nao ve nem armazena senha.
4. Agente so le e resume.

Fase 3:

1. Evoluir assistente local de leitura, se autorizado.
2. Avaliar cooperacao institucional com solucoes existentes apenas como referencia.
3. Continuar proibindo atos oficiais automaticos.
4. Manter geracao de minutas fora do SEI.

## Regra para implementar no sistema

Todo registro interno do agente deve guardar:

```text
usuario_local
estacao
data_hora
origem
acao_solicitada
acao_executada
resultado
necessitou_revisao_humana
processo_sei_referenciado
documento_sei_referenciado
```

Mas nunca:

```text
senha_sei
token_de_sessao_sei
cookie_sei
credencial_pessoal
```
