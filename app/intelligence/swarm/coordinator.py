"""Orquestrador do Enxame (Swarm Coordinator).

Ele coordena a execução iterativa (loop) entre os agentes especialistas.
Baseado no modelo State Graph (similar ao LangGraph), garantindo que
a minuta passe por revisão crítica e redação até estar pronta ou atingir
o limite de tentativas.
"""

from app.intelligence.swarm.state import SwarmState
from app.intelligence.swarm.agents import TriageAgent, DraftAgent, CriticAgent

class SwarmCoordinator:
    """Orquestra o ciclo de vida e roteamento dos agentes."""
    
    def __init__(self):
        self.triage = TriageAgent()
        self.draft = DraftAgent()
        self.critic = CriticAgent()

    def run(self, processo_sei: str, titulo: str, texto: str, usuario: str) -> SwarmState:
        """Executa a máquina de estados (Workflow) do Enxame."""
        
        # 1. Inicializa o Estado Global
        state = SwarmState(
            processo_sei=processo_sei,
            titulo_documento=titulo,
            texto_processo=texto,
            usuario_local=usuario
        )
        state.log("Coordinator", "Swarm inicializado. Contexto carregado.")
        
        # 2. Nodo: Triagem
        state = self.triage.execute(state)
        
        # 3. Loop: Redação e Revisão (Self-Correction)
        while state.tentativas_redacao < state.max_tentativas:
            # Nodo: Redator
            state = self.draft.execute(state)
            
            # Nodo: Crítico
            state = self.critic.execute(state)
            
            # Condição de Roteamento (Aprovou? Sai do loop)
            if state.aprovado_pelo_critico:
                state.log("Coordinator", "Ciclo de revisão encerrado. Resultado aprovado.")
                break
                
            state.log("Coordinator", f"Crítica recebida. Iniciando iteração {state.tentativas_redacao + 1}.")
            
        if not state.aprovado_pelo_critico:
            state.log("Coordinator", "Atingido limite de tentativas sem aprovação final. Devolvendo última versão para julgamento humano.")
            
        return state
