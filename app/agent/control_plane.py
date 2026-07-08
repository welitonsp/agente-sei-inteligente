"""Control Plane de missoes supervisionadas do Agente 19.

Esta camada define contratos estaveis para missoes, propostas de acao,
aprovacoes humanas, chamadas de ferramenta e auditoria sanitizada. Ela nao
executa ato oficial no SEI: apenas decide, registra e bloqueia antes de qualquer
ferramenta externa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from app.core import permissions
from app.sei.sei_action_guard import (
    GuardDecision,
    GuardRequest,
    GuardResult,
    evaluate,
)


class MissionStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    NEEDS_HUMAN_INPUT = "needs_human_input"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FORBIDDEN = "forbidden"


_OFFICIAL_ACTION_NAMES = frozenset(action.value for action in permissions.FORBIDDEN_ACTIONS)
_SENSITIVE_KEYS = (
    "texto",
    "conteudo",
    "body",
    "senha",
    "password",
    "cookie",
    "token",
    "session",
    "sessao",
    "authorization",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in _SENSITIVE_KEYS):
                sanitized[str(key)] = "[REDACTED]"
            else:
                sanitized[str(key)] = _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    return value


@dataclass(frozen=True)
class ToolPolicy:
    name: str
    description: str
    risk_level: RiskLevel
    read_only: bool
    requires_human_approval: bool
    writes_external_system: bool
    writes_sei: bool
    allowed_actions: tuple[str, ...] = ()

    def to_contract(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "read_only": self.read_only,
            "requires_human_approval": self.requires_human_approval,
            "writes_external_system": self.writes_external_system,
            "writes_sei": self.writes_sei,
            "allowed_actions": list(self.allowed_actions),
        }


@dataclass(frozen=True)
class MissionStep:
    name: str
    status: MissionStatus = MissionStatus.DRAFT
    owner_agent: str = ""
    summary: str = ""

    def to_contract(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status.value,
            "owner_agent": self.owner_agent,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    action: str
    status: str
    input_hash: str = ""
    output_hash: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    guard_decision: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "action": self.action,
            "status": self.status,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "risk_level": self.risk_level.value,
            "guard_decision": _sanitize(self.guard_decision),
        }


@dataclass(frozen=True)
class AgentRun:
    agent_name: str
    mission_id: str
    status: MissionStatus
    started_at: str = field(default_factory=_now_iso)
    finished_at: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    def to_contract(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "mission_id": self.mission_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "tool_calls": [call.to_contract() for call in self.tool_calls],
        }


@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    mission_id: str
    tool_name: str
    action: str
    title: str
    rationale: str
    risk_level: RiskLevel
    requires_human_approval: bool = True
    writes_external_system: bool = False
    writes_sei: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "mission_id": self.mission_id,
            "tool_name": self.tool_name,
            "action": self.action,
            "title": self.title,
            "rationale": self.rationale,
            "risk_level": self.risk_level.value,
            "requires_human_approval": self.requires_human_approval,
            "writes_external_system": self.writes_external_system,
            "writes_sei": self.writes_sei,
            "metadata": _sanitize(self.metadata),
        }


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    mission_id: str
    proposal_id: str
    required: bool
    reason: str
    approved_by: str = ""
    approved_at: str = ""
    content_hash: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "mission_id": self.mission_id,
            "proposal_id": self.proposal_id,
            "required": self.required,
            "reason": self.reason,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    mission_id: str
    event_type: str
    status: str
    created_at: str = field(default_factory=_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "mission_id": self.mission_id,
            "event_type": self.event_type,
            "status": self.status,
            "created_at": self.created_at,
            "metadata": _sanitize(self.metadata),
        }


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    mission_id: str
    proposal_id: str
    decision: str
    reason: str
    guard: dict[str, Any]
    decided_at: str = field(default_factory=_now_iso)

    def to_contract(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "mission_id": self.mission_id,
            "proposal_id": self.proposal_id,
            "decision": self.decision,
            "reason": self.reason,
            "guard": _sanitize(self.guard),
            "decided_at": self.decided_at,
        }


@dataclass(frozen=True)
class Mission:
    mission_id: str
    title: str
    status: MissionStatus
    steps: list[MissionStep] = field(default_factory=list)
    action_proposals: list[ActionProposal] = field(default_factory=list)
    approvals: list[ApprovalRequest] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    audit_events: list[AuditEvent] = field(default_factory=list)

    def to_contract(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "status": self.status.value,
            "steps": [step.to_contract() for step in self.steps],
            "action_proposals": [p.to_contract() for p in self.action_proposals],
            "approval_requests": [a.to_contract() for a in self.approvals],
            "decisions": [d.to_contract() for d in self.decisions],
            "audit_events": [e.to_contract() for e in self.audit_events],
        }


TOOL_REGISTRY: dict[str, ToolPolicy] = {
    "mission_control": ToolPolicy(
        name="mission_control",
        description="Coordena analise, triagem, riscos e minuta local.",
        risk_level=RiskLevel.LOW,
        read_only=True,
        requires_human_approval=False,
        writes_external_system=False,
        writes_sei=False,
        allowed_actions=(
            "RESUMIR",
            "CLASSIFICAR",
            "IDENTIFICAR_PRAZO",
            "GERAR_MINUTA",
        ),
    ),
    "calendar_agent": ToolPolicy(
        name="calendar_agent",
        description="Prepara evento Google Agenda mediante aprovacao humana.",
        risk_level=RiskLevel.MEDIUM,
        read_only=False,
        requires_human_approval=True,
        writes_external_system=True,
        writes_sei=False,
        allowed_actions=("CRIAR_EVENTO_AGENDA",),
    ),
    "notification_agent": ToolPolicy(
        name="notification_agent",
        description="Prepara alerta Telegram/e-mail mediante aprovacao humana.",
        risk_level=RiskLevel.MEDIUM,
        read_only=False,
        requires_human_approval=True,
        writes_external_system=True,
        writes_sei=False,
        allowed_actions=("ENVIAR_ALERTA",),
    ),
}


def new_mission_id() -> str:
    return f"mis19-{uuid4().hex[:16]}"


def new_proposal_id() -> str:
    return f"ap19-{uuid4().hex[:16]}"


def list_tool_policies() -> list[dict[str, Any]]:
    return [tool.to_contract() for tool in TOOL_REGISTRY.values()]


def get_tool_policy(tool_name: str) -> ToolPolicy:
    try:
        return TOOL_REGISTRY[tool_name]
    except KeyError as exc:
        raise PermissionError(f"Ferramenta nao registrada: {tool_name}") from exc


def build_action_proposal(
    *,
    mission_id: str,
    tool_name: str,
    action: str,
    title: str,
    rationale: str,
    metadata: dict[str, Any] | None = None,
) -> ActionProposal:
    tool = get_tool_policy(tool_name)
    normalized_action = action.strip().upper()
    risk = RiskLevel.FORBIDDEN if normalized_action in _OFFICIAL_ACTION_NAMES else tool.risk_level
    return ActionProposal(
        proposal_id=new_proposal_id(),
        mission_id=mission_id,
        tool_name=tool.name,
        action=normalized_action,
        title=title,
        rationale=rationale,
        risk_level=risk,
        requires_human_approval=tool.requires_human_approval,
        writes_external_system=tool.writes_external_system,
        writes_sei=tool.writes_sei,
        metadata=metadata or {},
    )


def evaluate_action_proposal(
    proposal: ActionProposal,
    *,
    approved_by_human: bool = False,
    usuario_local: str = "",
    processo_sei: str = "",
) -> DecisionRecord:
    tool = get_tool_policy(proposal.tool_name)
    if proposal.action not in tool.allowed_actions:
        guard = GuardResult(
            permitido=False,
            decisao=GuardDecision.BLOQUEADO,
            motivo="Acao fora do escopo da ferramenta registrada.",
            acao=proposal.action,
            revisao_humana_obrigatoria=True,
            metadata={"regra": "tool_scope_default_deny"},
        )
    else:
        guard = evaluate(
            GuardRequest(
                acao_solicitada=proposal.action,
                origem=f"control_plane:{proposal.tool_name}",
                usuario_local=usuario_local,
                processo_sei=processo_sei,
                justificativa=proposal.rationale,
                aprovado_por_humano=approved_by_human,
            )
        )
    decision = "approved" if guard.permitido else guard.decisao.value
    return DecisionRecord(
        decision_id=f"dec19-{uuid4().hex[:16]}",
        mission_id=proposal.mission_id,
        proposal_id=proposal.proposal_id,
        decision=decision,
        reason=guard.motivo,
        guard=guard.to_contract() | {"metadata": _sanitize(guard.metadata)},
    )


def build_supervised_mission(
    *,
    mission_id: str,
    title: str,
    proposals: list[ActionProposal],
    decisions: list[DecisionRecord],
    ready: bool,
) -> Mission:
    blocked = any(decision.decision == "bloqueado" for decision in decisions)
    status = MissionStatus.BLOCKED if blocked else MissionStatus.READY_FOR_REVIEW
    if not ready and not blocked:
        status = MissionStatus.NEEDS_HUMAN_INPUT
    approval_requests = [
        ApprovalRequest(
            approval_id=f"apr19-{uuid4().hex[:16]}",
            mission_id=proposal.mission_id,
            proposal_id=proposal.proposal_id,
            required=proposal.requires_human_approval,
            reason="Aprovacao humana exigida antes de efeito externo.",
        )
        for proposal in proposals
        if proposal.requires_human_approval
    ]
    return Mission(
        mission_id=mission_id,
        title=title,
        status=status,
        steps=[
            MissionStep(
                name="triagem",
                status=MissionStatus.READY_FOR_REVIEW,
                owner_agent="triage_agent",
                summary="Classificacao local sem ato oficial.",
            ),
            MissionStep(
                name="minuta",
                status=MissionStatus.READY_FOR_REVIEW,
                owner_agent="draft_agent",
                summary="Rascunho local para revisao humana.",
            ),
            MissionStep(
                name="aprovacao",
                status=MissionStatus.NEEDS_HUMAN_INPUT,
                owner_agent="human_operator",
                summary="Ato oficial permanece manual.",
            ),
        ],
        action_proposals=proposals,
        approvals=approval_requests,
        decisions=decisions,
        audit_events=[
            AuditEvent(
                event_id=f"aud19-{uuid4().hex[:16]}",
                mission_id=mission_id,
                event_type="control_plane_built",
                status=status.value,
                metadata={"texto_integral_persistido": False},
            )
        ],
    )
