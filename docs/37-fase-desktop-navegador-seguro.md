# Fase 37.2 - Agente 19 Desktop com Navegador Seguro

Data: 2026-06-22
Status: PROTOTIPO_IMPLEMENTADO

## Contexto

O ambiente institucional pode impedir a instalacao de extensao Chrome/Edge.
Tambem foi levantada a possibilidade de o usuario informar login e senha do
SEI dentro do Agente 19.

Essa alternativa fica recusada por seguranca: o Agente 19 nao deve solicitar,
receber, armazenar, registrar, interceptar ou processar usuario e senha do SEI.
Tambem nao deve capturar cookies, sessao, localStorage, sessionStorage, headers
de autenticacao, tokens ou qualquer credencial.

## Decisao

Criar uma aplicacao desktop local chamada Agente 19 Desktop. Ela pode abrir o
SEI pela URL oficial:

```text
https://sei.go.gov.br/sei/
```

O login deve ocorrer exclusivamente na pagina oficial do SEI, controlada pelo
usuario. O Agente 19 fica em janela local ao lado, recebendo apenas texto colado
manualmente ou PDF exportado manualmente.

Aviso fixo da aplicacao:

```text
O login é realizado exclusivamente na página oficial do SEI. O Agente 19 não captura senha, cookie, sessão ou credenciais e não pratica atos oficiais.
```

## Arquitetura

| Componente | Papel |
| --- | --- |
| `app.desktop` | Janela desktop local do Agente 19 |
| Navegador oficial/separado | Abre `https://sei.go.gov.br/sei/` para login direto do usuario |
| Backend local | Continua em `http://127.0.0.1:8000` |
| Intake texto | Analisa texto copiado manualmente do SEI |
| Intake PDF | Analisa PDF exportado manualmente do SEI |
| Extensao Chrome/Edge | Mantida como recurso futuro opcional, dependente de autorizacao institucional |

## Fluxo permitido

1. Usuario abre o Agente 19 Desktop.
2. O backend local sobe em `127.0.0.1`.
3. Usuario clica em `Abrir SEI oficial`.
4. O login acontece diretamente na pagina oficial do SEI.
5. Usuario copia manualmente texto do SEI ou exporta manualmente PDF.
6. Usuario cola o texto ou seleciona o PDF no Agente 19.
7. O Agente 19 envia a demanda ao backend local.
8. O Agente 19 exibe resumo, tipo provavel, evento/prazo, providencia sugerida e botao de copiar resultado.
9. Qualquer ato oficial continua manual no SEI.

## Capacidades liberadas no prototipo

- [x] Abrir aplicacao desktop local.
- [x] Abrir SEI pela URL oficial em navegador/janela separada.
- [x] Manter aviso fixo de seguranca.
- [x] Colar texto copiado manualmente do SEI.
- [x] Selecionar PDF exportado manualmente do SEI.
- [x] Analisar texto via backend local.
- [x] Analisar PDF via backend local.
- [x] Gerar resumo preliminar.
- [x] Identificar tipo provavel.
- [x] Detectar prazo/evento por heuristica local.
- [x] Sugerir providencia conservadora.
- [x] Copiar resultado.
- [x] Bloquear payload com campos/indicios de credencial.
- [x] Testar que nao existem campos de senha/login SEI no Agente 19.

## Proibido

- [ ] Pedir usuario do SEI.
- [ ] Pedir senha do SEI.
- [ ] Salvar usuario ou senha do SEI.
- [ ] Ler cookies.
- [ ] Ler sessao.
- [ ] Ler localStorage/sessionStorage.
- [ ] Capturar headers de autenticacao.
- [ ] Capturar token.
- [ ] Automatizar cliques.
- [ ] Assinar documento.
- [ ] Tramitar processo.
- [ ] Enviar processo.
- [ ] Criar documento oficial no SEI.
- [ ] Inserir conteudo no SEI sem acao humana.
- [ ] Burlar politica de extensao ou seguranca do navegador.

## Como executar

```bat
.venv\Scripts\python.exe -m app.desktop
```

O desktop sobe o backend local se ele ainda nao estiver ativo. Alternativamente,
o backend pode ser iniciado antes:

```bat
.venv\Scripts\python.exe -m app.dashboard
```

## Criterios de aceite

- [x] O Agente 19 abre como aplicacao local.
- [x] O SEI pode ser aberto em janela separada pela URL oficial.
- [x] O usuario faz login apenas na pagina oficial do SEI.
- [x] O agente funciona sem extensao.
- [x] O agente nao captura credenciais.
- [x] O agente nao executa atos oficiais.
- [x] Testes automatizados de contrato foram criados.
- [ ] Uso com navegador interno/separado homologado pela instituicao antes de producao real.

## Homologacao pendente

O uso real do desktop com navegador interno ou janela separada precisa de
homologacao/autorizacao institucional antes de producao. Ate la, o uso deve
ficar restrito a ambiente local controlado e exemplos anonimizados.
