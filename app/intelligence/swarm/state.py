"""Definição do estado global que trafega entre os múltiplos agentes do Swarm.

Este estado mantém o contexto do processo SEI e as contribuições iterativas
dos agentes (Triador, Redator, Crítico).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class SwarmState:
    # Contexto Inicial
    processo_sei: str
    titulo_documento: str
    texto_processo: str
    usuario_local: str
    
    # Contribuições dos Agentes
    intencao_detectada: str = ""
    resumo: str = ""
    providencia_sugerida: str = ""
    minuta_rascunho: str = ""
    tipo_minuta: str = ""
    
    # Controle e Revisão
    revisao_critica: str = ""
    aprovado_pelo_critico: bool = False
    tentativas_redacao: int = 0
    max_tentativas: int = 3
    
    # Rastreabilidade (Auditoria)
    trace_log: list[str] = field(default_factory=list)
    
    def log(self, agente: str, mensagem: str) -> None:
        """Registra um passo na auditoria do Swarm."""
        self.trace_log.append(f"[{agente}] {mensagem}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "processo_sei": self.processo_sei,
            "intencao_detectada": self.intencao_detectada,
            "aprovado_pelo_critico": self.aprovado_pelo_critico,
            "minuta_rascunho": self.minuta_rascunho,
            "trace": self.trace_log,
        }
