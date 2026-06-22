# Checklist Consolidado - Funcionário Digital de IA

Este checklist deve ser validado continuamente para garantir a integridade do Agente 19 como Funcionário Digital de IA do 19º CRPM, garantindo sua utilidade administrativa e sua completa adesão às regras de segurança institucionais.

## Identidade e Credenciais
- [x] O Agente NÃO pede senha do SEI.
- [x] O Agente NÃO armazena senha.
- [x] O Agente NÃO armazena cookie ou sessão.
- [x] O Agente NÃO captura token de autenticação.
- [ ] O login é feito exclusivamente na página oficial do SEI pelo próprio servidor.

## Atuação no Processo SEI
- [ ] O servidor copia e informa o número do processo ao Agente 19 por meio de janela/logo flutuante.
- [ ] O Agente utiliza a sessão do usuário (sem capturar credenciais de forma persistente) para ler o processo aberto no navegador.
- [ ] O Agente exporta o processo em PDF e analisa o PDF inteiro.
- [ ] O Agente identifica corretamente assunto, origem, interessado, prazo, evento, urgência, unidade envolvida, impacto para o 19º CRPM e providência recomendada.

## Criação de Minutas e Atos Oficiais
- [ ] O Agente pergunta proativamente ao usuário qual tipo de documento criar (ex: Ofício, Despacho, Ordem de Atendimento) antes de qualquer inserção.
- [ ] A criação de minuta no SEI exige confirmação humana explícita.
- [ ] O Agente cria e preenche a minuta de forma assistida, mas **NÃO a assina**.
- [ ] O Agente emite aviso claro de que a minuta está pronta para revisão.
- [ ] O humano revisa, corrige, assina e tramita manualmente.
- [ ] O Agente **NÃO tramita**, NÃO conclui, NÃO exclui e NÃO cancela documentos ou processos.
- [ ] O Agente **NÃO dá ciência automática** nem envia processos sem ação do servidor.

## Aprendizado
- [x] O Agente possui um módulo de memória institucional, registrando precedentes da unidade.
- [x] O Agente aprende de maneira supervisionada com as revisões e correções feitas pelos humanos na redação.
- [x] O Agente não usa informações do aprendizado de maneira violadora da Política de Identidade e Dados do SEI.
