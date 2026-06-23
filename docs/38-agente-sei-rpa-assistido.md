# FASE 38 — Agente SEI RPA Assistido por Número de Processo

## Visão Geral
Esta fase define o fluxo de automação assistida onde o Agente 19 atua a partir do número de um processo no SEI. A automação RPA é estritamente assistida e opera de forma transparente sob o comando de um servidor.

## O Fluxo Desejado
1. O servidor entra no SEI normalmente com seu usuário e senha.
2. O login ocorre exclusivamente na página oficial do SEI.
3. O Agente 19 não pede, não salva e não processa senha, cookie, sessão ou token.
4. O servidor vê um novo processo no SEI.
5. O servidor copia o número do processo.
6. O servidor aciona o Agente 19 por uma janela/logo flutuante.
7. O servidor informa o número do processo.
8. O Agente, usando a sessão já autenticada pelo usuário, abre o processo no SEI.
9. O Agente exporta o processo em PDF.
10. O Agente analisa o PDF inteiro.
11. O Agente identifica assunto, origem, interessado, prazo, evento, urgência, unidade envolvida, impacto para o 19º CRPM e providência recomendada.
12. O Agente pergunta se o usuário deseja criar Ofício, Despacho, Ordem de Atendimento ou outro documento.
13. Após confirmação humana, o Agente cria a minuta dentro do SEI.
14. O Agente preenche a minuta, mas não assina.
15. O Agente avisa que a minuta está pronta para revisão.
16. O humano revisa, corrige, assina e tramita manualmente.

## Restrições Críticas de RPA
- O sistema **exige** confirmação humana para a criação de minutas.
- O Agente atua apenas na preparação do texto, preenchendo rascunhos.
- O Agente **NUNCA** realiza o ato oficial de assinatura.
- O Agente **NUNCA** tramita, conclui ou envia processos de forma automática.
