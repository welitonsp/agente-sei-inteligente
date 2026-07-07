"""Tracing operacional sanitizado do Agente 19."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class AgentTraceStep:
    etapa: str
    status: str
    detalhe: str = ""

    def to_contract(self) -> dict[str, str]:
        return {
            "etapa": self.etapa,
            "status": self.status,
            "detalhe": self.detalhe,
        }


@dataclass(frozen=True)
class AgentTrace:
    trace_id: str
    started_at: str
    passos: list[AgentTraceStep] = field(default_factory=list)

    def add(self, etapa: str, status: str, detalhe: str = "") -> "AgentTrace":
        return AgentTrace(
            trace_id=self.trace_id,
            started_at=self.started_at,
            passos=[*self.passos, AgentTraceStep(etapa, status, detalhe)],
        )

    def to_contract(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "passos": [step.to_contract() for step in self.passos],
        }


def start_agent_trace(trace_id: str = "") -> AgentTrace:
    return AgentTrace(
        trace_id=trace_id.strip() or f"agt19-{uuid4().hex[:16]}",
        started_at=datetime.now(timezone.utc).isoformat(),
    )
