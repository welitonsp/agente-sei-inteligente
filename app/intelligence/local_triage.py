"""Triagem e roteamento local do 19 CRPM por regras da knowledge base."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core import audit
from app.intelligence.knowledge_base import (
    DEFAULT_KB_PATH,
    LocalKnowledgeBase,
    RoutingRule,
    load_knowledge_base,
)
from app.sei.sei_action_guard import GuardRequest, evaluate


_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class TriageRequest:
    assunto: str
    texto: str = ""
    processo_sei: str = ""
    usuario_local: str = ""
    estacao: str = ""
    origem: str = "triagem_local"
    kb_path: str | Path = DEFAULT_KB_PATH


@dataclass(frozen=True)
class TriageResult:
    status: str
    interesse_19crpm: str
    nivel_prioridade: str
    unidade_sugerida: str
    tipo_minuta_sugerido: str
    providencia_sugerida: str
    justificativa: str
    regra_aplicada: str
    alternativas: list[str]
    campos_pendentes: list[str]
    revisao_humana_obrigatoria: bool
    confianca: float
    audit_log_ids: list[int] = field(default_factory=list)

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resultado": {
                "interesse_19crpm": self.interesse_19crpm,
                "nivel_prioridade": self.nivel_prioridade,
                "unidade_sugerida": self.unidade_sugerida,
                "tipo_minuta_sugerido": self.tipo_minuta_sugerido,
                "providencia_sugerida": self.providencia_sugerida,
                "justificativa": self.justificativa,
                "regra_aplicada": self.regra_aplicada,
                "alternativas": self.alternativas,
            },
            "confianca": self.confianca,
            "fontes": ["knowledge_base_local"] if self.regra_aplicada else [],
            "campos_pendentes": self.campos_pendentes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_sugeridas": ["REVISAR_TRIAGEM"],
            "acoes_bloqueadas": [
                "DECIDIR_UNIDADE_SEM_REGRA",
                "TRAMITAR_PROCESSO",
                "ENVIAR_PROCESSO",
            ],
            "logs": self.audit_log_ids,
        }


def analyze_triage(request: TriageRequest) -> TriageResult:
    kb = load_knowledge_base(request.kb_path)
    guard_req = GuardRequest(
        acao_solicitada="CLASSIFICAR",
        origem=request.origem,
        usuario_local=request.usuario_local,
        estacao=request.estacao,
        processo_sei=request.processo_sei,
        justificativa="Triagem local por regras da knowledge base do 19 CRPM.",
        aprovado_por_humano=False,
    )
    guard_res = evaluate(guard_req)
    audit_ids = [audit.record_guard_decision(guard_req, guard_res)]
    if not guard_res.permitido:
        return _indefinido(
            request,
            audit_ids,
            "Guardiao bloqueou a classificacao local.",
            ["guardiao"],
        )

    text = _normalize(f"{request.assunto} {request.texto}")
    if not text:
        return _indefinido(
            request,
            audit_ids,
            "Texto/assunto ausente para triagem.",
            ["assunto", "texto"],
        )
    if not kb.has_real_rules:
        return _indefinido(
            request,
            audit_ids,
            "Knowledge base local ainda nao possui regras reais.",
            ["knowledge_base_regras"],
        )

    matched_rule = _match_routing_rule(text, kb)
    if matched_rule:
        return _from_routing_rule(request, kb, matched_rule, audit_ids)

    interest, keyword_confidence = _interest_from_keywords(text, kb)
    audit_ids.append(
        audit.record(
            action="CLASSIFICAR",
            result="precisa_revisao",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Palavras-chave encontradas sem regra de direcionamento clara.",
            metadata={
                "origem": request.origem,
                "interesse_19crpm": interest,
                "confianca": keyword_confidence,
                "unidade_sugerida": "",
            },
        )
    )
    return TriageResult(
        status="precisa_revisao",
        interesse_19crpm=interest,
        nivel_prioridade="normal",
        unidade_sugerida="",
        tipo_minuta_sugerido="",
        providencia_sugerida="Revisar manualmente; nao ha regra de direcionamento clara.",
        justificativa="Ha indicios por palavra-chave, mas nenhuma regra valida definiu unidade.",
        regra_aplicada="",
        alternativas=[],
        campos_pendentes=["regra_direcionamento", "unidade_destino"],
        revisao_humana_obrigatoria=True,
        confianca=keyword_confidence,
        audit_log_ids=audit_ids,
    )


def _from_routing_rule(
    request: TriageRequest,
    kb: LocalKnowledgeBase,
    rule: RoutingRule,
    audit_ids: list[int],
) -> TriageResult:
    pending = []
    unidade = rule.unidade_destino
    if unidade and not kb.has_unit(unidade):
        pending.append("unidade_destino_nao_cadastrada")
        unidade = ""
    if not unidade:
        pending.append("unidade_destino")

    confidence = min(max(rule.confianca or 0.55, 0.2), 0.85)
    status = "precisa_revisao"
    audit_ids.append(
        audit.record(
            action="CLASSIFICAR",
            result=status,
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason="Triagem local por regra; revisao humana obrigatoria.",
            metadata={
                "origem": request.origem,
                "regra_aplicada": rule.id,
                "interesse_19crpm": rule.interesse,
                "unidade_sugerida": unidade,
                "tipo_minuta": rule.tipo_minuta,
                "confianca": confidence,
                "campos_pendentes": pending,
            },
        )
    )
    return TriageResult(
        status=status,
        interesse_19crpm=rule.interesse or "indefinido",
        nivel_prioridade="normal" if rule.prioridade < 80 else "alta",
        unidade_sugerida=unidade,
        tipo_minuta_sugerido=rule.tipo_minuta,
        providencia_sugerida=rule.providencia
        or "Revisar regra aplicada e definir providencia.",
        justificativa=f"Regra local '{rule.id or 'sem_id'}' aplicada por termo configurado.",
        regra_aplicada=rule.id,
        alternativas=[],
        campos_pendentes=pending,
        revisao_humana_obrigatoria=True,
        confianca=confidence if not pending else min(confidence, 0.45),
        audit_log_ids=audit_ids,
    )


def _match_routing_rule(text: str, kb: LocalKnowledgeBase) -> RoutingRule | None:
    for rule in kb.regras_direcionamento:
        terms = [_normalize(term) for term in rule.termos]
        if any(term and term in text for term in terms):
            return rule
    return None


def _interest_from_keywords(text: str, kb: LocalKnowledgeBase) -> tuple[str, float]:
    best_interest = "indefinido"
    best_weight = 0.0
    for rule in kb.palavras_chave:
        term = _normalize(rule.termo)
        if term and term in text and rule.peso >= best_weight:
            best_interest = rule.interesse or "indefinido"
            best_weight = rule.peso
    confidence = min(0.55, max(0.2, best_weight / 10)) if best_weight else 0.1
    return best_interest, round(confidence, 2)


def _indefinido(
    request: TriageRequest,
    audit_ids: list[int],
    reason: str,
    pending: list[str],
) -> TriageResult:
    audit_ids.append(
        audit.record(
            action="CLASSIFICAR",
            result="precisa_revisao",
            actor_id=request.usuario_local or None,
            target_type="processo_sei",
            target_id=request.processo_sei or None,
            reason=reason,
            metadata={
                "origem": request.origem,
                "interesse_19crpm": "indefinido",
                "unidade_sugerida": "",
                "campos_pendentes": pending,
            },
        )
    )
    return TriageResult(
        status="precisa_revisao",
        interesse_19crpm="indefinido",
        nivel_prioridade="normal",
        unidade_sugerida="",
        tipo_minuta_sugerido="",
        providencia_sugerida="Preencher/revisar knowledge base antes de direcionar.",
        justificativa=reason,
        regra_aplicada="",
        alternativas=[],
        campos_pendentes=pending,
        revisao_humana_obrigatoria=True,
        confianca=0.0,
        audit_log_ids=audit_ids,
    )


def _normalize(value: str) -> str:
    return _SPACE.sub(" ", value.strip().lower())
