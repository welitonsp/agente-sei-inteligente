# Politica de dados extraidos do SEI

## Objetivo

Definir como textos, PDFs, metadados e resumos extraidos do SEI podem ser tratados pelo Agente SEI Inteligente.

## Regra principal

Por padrao, conteudo extraido de processo/documento SEI deve permanecer local e temporario.

Configuracao padrao:

```text
SEI_DATA_MODE=local_only
SEI_TEXT_RETENTION=ephemeral
SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT=false
```

## Classificacao dos dados

| Tipo | Exemplo | Tratamento |
| --- | --- | --- |
| Credencial | senha, cookie, token, sessao | Nunca coletar, nunca salvar |
| Metadado minimo | numero do processo, numero do documento, data | Pode registrar em log |
| Texto de documento | conteudo copiado, PDF, despacho, oficio | Local e temporario por padrao |
| Resumo | resumo gerado pelo agente | Pode salvar se autorizado |
| Minuta | texto criado para revisao | Pode salvar como rascunho interno |
| Anexo sensivel | documento restrito/sigiloso | Exigir revisao e politica especifica |

## O que nunca salvar

```text
senha_sei
cookie_sei
token_de_sessao_sei
credencial_pessoal
html_completo_com_sessao
cabecalhos_de_autenticacao
```

## Uso de IA externa

Gemini ou outro provedor externo pode ser usado para:

1. Manual do Usuario SEI.
2. Manual WebServices SEI.
3. Modelos administrativos publicos ou autorizados.
4. Fluxos internos anonimizados.

Conteudo vivo extraido de processos SEI nao deve ser enviado para IA externa sem autorizacao formal.

Se a autorizacao existir, exigir:

1. Classificacao do tipo de dado.
2. Ciencia do usuario.
3. Reducao de dados ao minimo necessario.
4. Registro de log.
5. Possibilidade de anonimizar nomes, CPFs, telefones, enderecos e dados pessoais.

## Retencao

Modo recomendado para MVP:

```text
ephemeral
```

Significa:

1. Texto completo usado apenas durante a analise.
2. Nao salvar HTML completo do SEI.
3. Salvar apenas resumo, metadados minimos, resultado da analise e log.
4. Permitir descarte manual pelo operador.

Modos futuros possiveis:

```text
no_store
ephemeral
save_summary_only
save_full_text_authorized
```

## Logs permitidos

Registrar:

```text
request_id
usuario_local
estacao
data_hora
processo_sei
documentos_referenciados
skills_chamadas
resultado
confianca
revisao_humana_obrigatoria
acoes_bloqueadas
```

Nao registrar:

```text
senha
cookie
token
conteudo integral sem necessidade
documento sigiloso integral
```

## Extensao de navegador

Se houver extensao read-only:

1. Ativar somente no dominio autorizado do SEI.
2. Ler apenas quando o servidor clicar no robozinho.
3. Nao enviar cookies ou tokens ao backend.
4. Nao salvar HTML completo.
5. Nao rodar em segundo plano sem acao do usuario.
6. Mostrar aviso de que a analise usa a sessao do servidor.
7. Permitir cancelar a leitura antes do envio ao backend local.

## Banco de dados

No MVP, salvar preferencialmente:

1. Metadados.
2. Hash do texto/documento.
3. Resumo.
4. Resultado estruturado.
5. Logs.

Evitar salvar:

1. Texto integral do documento.
2. PDF bruto.
3. HTML do SEI.

Se for necessario salvar texto integral, exigir configuracao explicita e justificativa operacional.

## Revisao humana obrigatoria

Exigir revisao quando:

1. Documento for restrito ou sigiloso.
2. Houver dados pessoais sensiveis.
3. O agente nao conseguir ler todos os documentos relevantes.
4. O texto for enviado por copia manual incompleta.
5. Houver baixa confianca.
6. Houver possibilidade de prazo.

