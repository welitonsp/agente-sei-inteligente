"""Servico de auditoria: registra acoes do agente de forma rastreavel e segura.

Cada registro guarda quem pediu, qual acao, sobre qual alvo, qual resultado e
o motivo. Todo conteudo passa pelo security_filter antes de ser persistido,
de modo que senha, cookie ou token nunca cheguem ao banco (docs/20, docs/25).
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.logging import get_logger, log_event
from app.core.security_filter import sanitize
from app.sei.sei_action_guard import GuardRequest, GuardResult
from app.storage.db import session_scope
from app.storage.models import AuditLog

_logger = get_logger("audit")


def record(
    *,
    action: str,
    result: str,
    actor_type: str = "agente",
    actor_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    """Persiste um registro de auditoria e devolve seu id.

    `metadata` e sanitizado antes de gravar. Tambem emite um log estruturado.
    """
    safe_meta = sanitize(metadata or {})

    with session_scope() as session:
        entry = AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            result=result,
            reason=reason,
            meta_json=safe_meta,
        )
        session.add(entry)
        session.flush()
        audit_id = entry.id

    log_event(
        _logger,
        logging.INFO if result == "permitido" else logging.WARNING,
        "audit",
        audit_id=audit_id,
        action=action,
        result=result,
        actor_id=actor_id,
        target_id=target_id,
        reason=reason,
    )
    return audit_id


def record_guard_decision(req: GuardRequest, res: GuardResult) -> int:
    """Atalho para auditar uma decisao do guard do SEI."""
    return record(
        action=res.acao,
        result=res.decisao.value,
        actor_type="agente",
        actor_id=req.usuario_local or None,
        target_type="processo_sei",
        target_id=req.processo_sei or None,
        reason=res.motivo,
        metadata={
            "origem": req.origem,
            "estacao": req.estacao,
            "justificativa": req.justificativa,
            "aprovado_por_humano": req.aprovado_por_humano,
            "revisao_humana_obrigatoria": res.revisao_humana_obrigatoria,
            **res.metadata,
        },
    )
