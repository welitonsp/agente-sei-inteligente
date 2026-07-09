"""Raciocinio de IA do grafo, roteado pela camada de provedor (Claude no controle).

Substitui o antigo `llm_gemini`. Diferencas de projeto:

1. **Guard antes de tudo**: toda geracao passa por `get_ai_provider()`, que
   consulta o `sei_action_guard` ANTES de qualquer chamada de rede. O prompt
   nunca e a barreira (ver `app/intelligence/ai_provider.py` e docs/53).
2. **Claude e o provedor padrao** (decisao registrada). O caminho offline usa o
   `EchoProvider`, deterministico e sem rede.
3. **Saidas estruturadas**: o critico devolve JSON e e **FAIL-CLOSED** — quando
   a auditoria automatica nao esta disponivel (offline) ou falha, ele NUNCA
   marca a minuta como aprovada; sinaliza indisponibilidade e exige revisao
   humana reforcada.
4. **Prompts versionados**: os system prompts vivem em `knowledge_base/prompts/`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.intake.manual_text import (
    ExtractedDeadline,
    ExtractedEvent,
    ManualTextRequest,
    ManualTextResult,
)
from app.intelligence.ai_provider import AIProvider, AIRole, get_ai_provider

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "knowledge_base" / "prompts"

_DEFAULT_RESUMO_SYSTEM = (
    "Voce e o Agente 19 do 19 CRPM. Produza um resumo executivo fiel (Fato, "
    "Prazo, Providencia), sem inventar dados e sem recomendar atos oficiais."
)
_DEFAULT_REVISAO_SYSTEM = (
    "Voce e o Auditor de Seguranca de IA do 19 CRPM. Responda apenas com JSON "
    '{"aprovado": bool, "feedback": str}. Reprove alucinacao, ato oficial ou '
    "exposicao de dado sensivel."
)


def _load_prompt(name: str, fallback: str) -> str:
    try:
        text = (_PROMPTS_DIR / name).read_text(encoding="utf-8").strip()
        return text or fallback
    except OSError:
        return fallback


def _extract_json(text: str) -> dict:
    """Extrai o primeiro objeto JSON de um texto, tolerante a cercas/ruido."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Resposta sem objeto JSON reconhecivel.")
    return json.loads(text[start : end + 1])


@dataclass(frozen=True)
class ReviewVerdict:
    """Veredicto do no critico.

    `disponivel=False` significa que a auditoria automatica nao rodou (offline
    ou erro). Nesse caso `aprovado` e sempre False (fail-closed): a decisao volta
    integralmente para o humano.
    """

    disponivel: bool
    aprovado: bool
    feedback: str


def summarize_process(
    titulo: str, texto: str, *, provider: AIProvider | None = None
) -> str:
    """Gera o resumo executivo do processo via papel logico RESUMO (Claude)."""
    provider = provider or get_ai_provider()
    system = _load_prompt("resumidor_administrativo.md", _DEFAULT_RESUMO_SYSTEM)
    prompt = (
        f"Titulo do documento: {titulo}\n\n"
        f"Conteudo:\n{texto}\n\n"
        "Produza o resumo executivo conforme as regras."
    )
    completion = provider.complete(AIRole.RESUMO, prompt, system=system)
    return completion.text.strip()


def review_minuta(
    texto_base: str,
    minuta_gerada: str,
    contexto: str,
    *,
    provider: AIProvider | None = None,
) -> ReviewVerdict:
    """Audita a minuta gerada. FAIL-CLOSED: erro/offline nunca aprova sozinho."""
    provider = provider or get_ai_provider()
    if not provider.is_real:
        return ReviewVerdict(
            disponivel=False,
            aprovado=False,
            feedback="Auditoria automatica indisponivel (provedor offline).",
        )

    system = _load_prompt("guardiao_seguranca.md", _DEFAULT_REVISAO_SYSTEM)
    prompt = (
        "Regras institucionais (RAG):\n"
        f"{contexto}\n\n"
        "Texto-base do processo:\n"
        f"{texto_base}\n\n"
        "Minuta gerada para auditar:\n"
        f"{minuta_gerada}\n\n"
        'Responda apenas com JSON {"aprovado": bool, "feedback": str}.'
    )
    try:
        completion = provider.complete(AIRole.REVISAO, prompt, system=system)
        data = _extract_json(completion.text)
        return ReviewVerdict(
            disponivel=True,
            aprovado=bool(data.get("aprovado")),
            feedback=str(data.get("feedback", "")).strip(),
        )
    except Exception as exc:  # rede, parse, guard: tudo cai em fail-closed
        return ReviewVerdict(
            disponivel=False,
            aprovado=False,
            feedback=f"Auditoria automatica falhou: {exc}",
        )


def analyze_manual_text(request: ManualTextRequest) -> ManualTextResult:
    """Analisa texto manual gerando resumo pela camada de IA (substitui Gemini).

    Mantem o contrato de `ManualTextResult` usado pelo painel. A extracao de
    evento/prazo permanece conservadora (False) como no fluxo anterior; o ganho
    aqui e rotear o resumo pelo provedor sob guarda, com fallback offline.
    """
    resumo = summarize_process(request.titulo, request.texto)
    text_hash = hashlib.sha256(request.texto.encode("utf-8")).hexdigest()
    return ManualTextResult(
        status="precisa_revisao",
        processo_id=None,
        documento_id=None,
        text_hash=text_hash,
        resumo_executivo=resumo,
        evento=ExtractedEvent(ha_evento=False),
        prazo=ExtractedDeadline(ha_prazo=False),
        campos_pendentes=[],
        revisao_humana_obrigatoria=True,
        confianca=0.9,
        audit_log_ids=[],
        motivo="Analise gerada pela camada de IA (Claude) sob guarda do SEI.",
    )


__all__ = [
    "ReviewVerdict",
    "analyze_manual_text",
    "review_minuta",
    "summarize_process",
]
