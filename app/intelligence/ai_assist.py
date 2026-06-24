"""Integração da camada de IA ao pipeline de análise (com fallback offline).

Liga os papéis lógicos (ver `ai_provider.py`) ao fluxo de leitura/análise,
respeitando duas barreiras:

1. **Guard de ações** — embutido em `provider.complete` (papel -> ação SEI).
2. **Política de dados** — `SEI_ALLOW_EXTERNAL_AI_FOR_LIVE_CONTENT` (padrão
   false). Conteúdo vivo do SEI só é enviado a uma IA **externa** (provedor
   real, ex.: Claude) quando essa flag estiver ligada. Caso contrário, usa-se o
   resumidor **local** offline. Provedores não-externos (Echo) não transmitem
   nada e não são gated por essa flag.

A saída de IA passa pelo sanitizador de PII antes de ser devolvida, mantendo a
mesma garantia do caminho local.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.core.config import Settings, get_settings
from app.intake.sanitizer import sanitize_text_preview
from app.intelligence.ai_provider import AIRole, AIProvider, get_ai_provider
from app.intelligence.institutional_analyzer import analyze_document_rules
from app.intelligence.summarizer import summarize

_SYSTEM_RESUMO = (
    "Você é um assessor administrativo do 19º CRPM. Resuma o documento do "
    "processo de forma fiel, objetiva e em português, sem inventar fatos, sem "
    "opinar e sem expor dados pessoais (CPF, telefone, e-mail). Máximo de 3 "
    "frases."
)


@dataclass(frozen=True)
class ResumoAssistido:
    """Resumo com proveniência: gerado por IA ou pelo resumidor local."""

    texto: str
    fonte: str  # "ia" | "local"
    modelo: str
    motivo: str = ""


def _pode_usar_ia_externa(provider: AIProvider, settings: Settings) -> bool:
    """IA externa (provedor real) exige a flag de conteúdo vivo ligada."""
    if not provider.is_real:
        return True  # Echo/offline não transmite nada externamente.
    return bool(settings.sei_allow_external_ai_for_live_content)


def resumo_assistido(
    texto: str,
    *,
    provider: AIProvider | None = None,
    settings: Settings | None = None,
) -> ResumoAssistido:
    """Gera um resumo via IA quando permitido; senão, resumo local offline."""
    cfg = settings or get_settings()
    prov = provider or get_ai_provider(cfg)

    if not _pode_usar_ia_externa(prov, cfg):
        return ResumoAssistido(
            texto=summarize(texto),
            fonte="local",
            modelo="local",
            motivo="ia_externa_desabilitada",
        )

    try:
        completion = prov.complete(AIRole.RESUMO, texto, system=_SYSTEM_RESUMO)
    except Exception as exc:  # rede/credencial/guard -> degrade gracioso
        return ResumoAssistido(
            texto=summarize(texto),
            fonte="local",
            modelo="local",
            motivo=f"falha_ia:{type(exc).__name__}",
        )

    texto_seguro = sanitize_text_preview(completion.text, max_length=600)
    return ResumoAssistido(texto=texto_seguro, fonte="ia", modelo=completion.model)


def analise_completa(
    texto: str,
    *,
    provider: AIProvider | None = None,
    settings: Settings | None = None,
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Análise local determinística + resumo assistido (IA quando permitido).

    Mantém todas as chaves de `analyze_document_rules` e substitui `resumo_curto`
    pelo resumo assistido, anexando a proveniência (`resumo_fonte`/`resumo_modelo`).
    """
    analise = analyze_document_rules(texto, reference_date=reference_date)
    resumo = resumo_assistido(texto, provider=provider, settings=settings)
    analise["resumo_curto"] = resumo.texto
    analise["resumo_fonte"] = resumo.fonte
    analise["resumo_modelo"] = resumo.modelo
    if resumo.motivo:
        analise["resumo_motivo"] = resumo.motivo
    return analise
