# Fase 41 - Diagnostico seguro de API SEI/WSSEI

## Objetivo

Verificar se a instancia do SEI Goias expõe algum endpoint publico provavel de
API/WSSEI, sem autenticar, sem capturar credenciais e sem depender de equipe de
TI para a primeira verificacao tecnica.

## Resultado

Foi criado um diagnostico seguro que testa apenas URLs candidatas:

1. `mod-wssei-v2`
2. `mod-wssei-v1`
3. `sei-soap-wsdl`

O diagnostico retorna somente:

1. nome do endpoint candidato;
2. URL consultada;
3. status HTTP;
4. classificacao;
5. detalhe tecnico sem credenciais.

## Comando

```bat
.venv\Scripts\python.exe scripts\sei_api_discovery.py
```

## Regras de seguranca

1. Nao envia usuario.
2. Nao envia senha.
3. Nao envia cookie.
4. Nao envia token.
5. Nao usa sessao do navegador.
6. Nao executa operacao de negocio.
7. Nao chama assinatura, tramitacao, envio, conclusao ou criacao de documento.
8. Resultado positivo nao autoriza uso real da API.

## Interpretacao

| Classificacao | Significado |
| --- | --- |
| `possivelmente_disponivel` | Endpoint respondeu sem autenticacao; ainda exige autorizacao antes de uso real |
| `existe_mas_bloqueado` | Endpoint parece existir, mas exige autenticacao/autorizacao |
| `nao_encontrado` | Endpoint candidato nao existe nesse caminho |
| `redireciona` | Endpoint redirecionou; precisa conferencia manual segura |
| `erro_servidor` | Servidor respondeu erro 5xx |
| `timeout` | Tempo limite excedido |
| `indisponivel` | Falha de rede/DNS |
| `inconclusivo` | Status nao classificado |

## Decisao

Este diagnostico pode ser usado para saber se ha pista de `mod-wssei` ou WSDL
nativo disponivel, mas nao substitui autorizacao institucional. Se o resultado
indicar endpoint existente, a proxima etapa e registrar evidencia e manter uso
real bloqueado ate validacao/autorizacao.
