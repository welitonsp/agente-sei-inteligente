# Registro de decisoes

Este documento registra decisoes oficiais do projeto.

## Formato

```text
ID:
Data:
Responsavel:
Status:
Contexto:
Decisao:
Motivo:
Impacto:
Risco:
Arquivos afetados:
Proximo passo:
```

## DEC-0001

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O modulo oficial SEI IA nao pode ser instalado no ambiente institucional.  
Decisao: Adotar arquitetura externa/local assistida, sem modulo interno no SEI.  
Motivo: Reduzir risco tecnico, institucional e de rastreabilidade.  
Impacto: Robozinho sera painel/extensao local read-only em fase futura; MVP usa texto colado e PDF.  
Risco: Menor integracao inicial com SEI.  
Arquivos afetados: `docs/21`, `docs/22`, `docs/25`, `docs/26`.  
Proximo passo: Implementar fundacao tecnica e painel MVP externo/local.

## DEC-0002

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O SEI registra a autoria das acoes por usuario.  
Decisao: Cada servidor deve usar seu proprio usuario e senha; o agente nao pode usar conta unica nem guardar senha.  
Motivo: Preservar rastreabilidade, responsabilidade e seguranca institucional.  
Impacto: O agente so atua apos autenticacao manual do servidor.  
Risco: Menos automacao, mais seguranca.  
Arquivos afetados: `docs/20`, `docs/21`, `docs/22`.  
Proximo passo: Manter bloqueio de login automatico em testes.

## DEC-0003

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: Conteudo real do SEI pode conter dados sensiveis.  
Decisao: Conteudo vivo do SEI nao deve ser enviado para IA externa sem autorizacao formal.  
Motivo: Protecao de dados e reducao de risco institucional.  
Impacto: MVP usa modo local/efemero; Gemini pode ser usado para manuais e materiais autorizados.  
Risco: Algumas analises podem exigir modelo local ou processamento limitado.  
Arquivos afetados: `docs/18`, `docs/25`, `.env.example`.  
Proximo passo: Implementar politica `SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT=false`.

## DEC-0004

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: Desenvolvimento com IA precisa de rastreabilidade.  
Decisao: Codigo de aplicacao deve entrar por branch e PR; commits diretos na main ficam restritos a documentacao enquanto nao houver codigo.  
Motivo: Controlar qualidade, seguranca e revisao humana.  
Impacto: Mudancas de codigo exigem PR, testes e revisao.  
Risco: Mais processo, menos improviso.  
Arquivos afetados: `docs/28`.  
Proximo passo: Configurar protecao da branch main quando o codigo iniciar.

## DEC-0005

Data: 2026-06-21  
Responsavel: Chefe do projeto  
Status: APROVADA  
Contexto: O projeto passara a usar Claude Code como agente de desenvolvimento assistido.  
Decisao: Criar e usar prompt mestre operacional para Claude Code, obrigando leitura da documentacao, respeito a matriz de conformidade, politica de dados, regras Git/IA e documentacao continua.  
Motivo: Evitar que o agente de codigo execute fora do escopo, pule seguranca ou perca rastreabilidade.  
Impacto: Claude Code deve iniciar pela fundacao tecnica e manter SEI real, robozinho real e IA externa com conteudo vivo fora do MVP.  
Risco: Prompt nao substitui revisao humana nem testes.  
Arquivos afetados: `docs/34-prompt-claude-code.md`, `README.md`.  
Proximo passo: Usar o prompt ao iniciar sessoes de desenvolvimento.
