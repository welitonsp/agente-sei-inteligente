# Governanca e riscos

## Papeis

| Papel | Responsabilidade |
| --- | --- |
| Chefe do projeto | Define prioridade, escopo e aceite |
| Responsavel tecnico | Implementa arquitetura, seguranca e integracoes |
| Operador administrativo | Usa o painel e valida demandas |
| Revisor/aprovador | Confere minutas e pratica atos oficiais |
| Administrador do sistema | Configura credenciais, usuarios e ambiente |

## Decisoes arquiteturais ja assumidas

1. O projeto sera redesenhado do zero.
2. A estrutura antiga, se existir, sera apenas referencia.
3. SQLite sera usado no inicio.
4. PostgreSQL fica como evolucao.
5. Google Agenda e Telegram entram antes do SEI.
6. SEI entra apenas em modo assistido.
7. Atos oficiais no SEI ficam proibidos para o agente.
8. A interface web sera o painel principal.

## Decisoes ainda abertas

1. Provedor de IA.
2. Provedor real do e-mail institucional.
3. Modelo de autenticacao do painel web.
4. Politica de retencao de logs.
5. Nivel permitido de escrita de rascunho no SEI.
6. Canal definitivo de alertas em celular.

## Riscos principais

| Risco | Impacto | Mitigacao |
| --- | --- | --- |
| IA interpretar prazo errado | Perda de prazo | Revisao humana quando confianca baixa e lembretes redundantes |
| Evento duplicado | Confusao operacional | Chave de duplicidade e log |
| Vazamento de credenciais | Alto | `.env`, segredo fora do repositorio e acesso restrito |
| Automacao indevida no SEI | Muito alto | Guarda de acoes, lista positiva e bloqueios testados |
| Dependencia de API paga | Custo | Provedor configuravel e opcao local |
| PDF sem texto | Falha de extracao | Marcar OCR necessario |
| Excesso de alertas | Fadiga operacional | Severidade, agrupamento e configuracao por tipo |
| Falha de agenda | Prazos sem registro | Log, retry e pendencia tecnica |

## Politica de mudanca

Mudancas que exigem aprovacao do chefe do projeto:

1. Habilitar qualquer escrita no SEI.
2. Trocar canal oficial de alerta.
3. Alterar regras de acoes proibidas.
4. Usar dados reais em ambiente de teste.
5. Expor painel fora da rede local.
6. Integrar API externa de IA com dados sensiveis.

## Criterio de parada

O agente deve parar e pedir revisao quando:

1. Houver acao proibida.
2. Faltar campo essencial.
3. Houver baixa confianca.
4. Documento tratar de decisao sensivel.
5. O SEI mostrar tela inesperada.
6. API externa retornar erro inconsistente.

## Indicadores de sucesso

1. Demandas processadas por dia.
2. Eventos criados sem correcao.
3. Prazos detectados corretamente.
4. Alertas entregues.
5. Minutas aproveitadas apos revisao.
6. Bloqueios de seguranca registrados.
7. Tempo medio entre recebimento e agenda.

