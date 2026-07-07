"""Módulo de Shadow Mode para Avaliação de Autonomia (Nível 1).

No Shadow Mode (Modo Sombra), o Agente de IA calcula um "Confidence Score"
e propõe uma ação oficial. O sistema não executa a ação, mas registra a
proposta e depois compara com o que o humano efetivamente realizou no SEI.

Isso cria um dataset rigoroso provando a segurança antes de evoluir
para a Autonomia Condicionada.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ShadowTrial:
    """Registro de uma proposta de IA vs. Ação final Humana."""
    
    trace_id: str
    processo_sei: str
    intencao_detectada: str
    acao_proposta_ia: str
    acao_real_humano: str | None = None
    confidence_score: float = 0.0
    match: bool | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc).isoformat())


class ShadowModeLogger:
    """Registra e calcula a acurácia das propostas em Shadow Mode."""
    
    def __init__(self, log_dir: str = ".shadow_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.log_file = self.log_dir / "shadow_trials.jsonl"
        
    def record_proposal(
        self, trace_id: str, processo: str, intencao: str, acao_proposta: str, confidence: float
    ) -> None:
        """Registra a ação oficial que a IA faria se tivesse autonomia plena."""
        trial = ShadowTrial(
            trace_id=trace_id,
            processo_sei=processo,
            intencao_detectada=intencao,
            acao_proposta_ia=acao_proposta,
            confidence_score=confidence,
        )
        self._append_log(trial)
        
    def record_human_action(self, trace_id: str, acao_real: str) -> None:
        """Registra a ação efetiva do humano para comparar com a IA."""
        # Na prática de produção, leríamos a linha correspondente, 
        # atualizaríamos o match e salvaríamos. 
        # Por simplicidade da Fase 1, anexamos o evento com a ação humana.
        trial = ShadowTrial(
            trace_id=trace_id,
            processo_sei="update",
            intencao_detectada="update",
            acao_proposta_ia="update",
            acao_real_humano=acao_real,
        )
        self._append_log(trial)

    def _append_log(self, trial: ShadowTrial) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(trial)) + "\n")
