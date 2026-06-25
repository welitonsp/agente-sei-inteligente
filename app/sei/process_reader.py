"""Leitor de processo do SEI (somente leitura, gated) — FASE 5C / Frente 2.

Lê o processo que o usuário já abriu na sessão logada, via `ReadOnlyPage`
(sem clicar, digitar ou escrever). Confere o número e devolve o conteúdo visível
+ os títulos da árvore de documentos, para o agente analisar.

Portões (verificados ANTES de abrir qualquer navegador):
1. `ENABLE_SEI_BROWSER_AUTOMATION` precisa estar ligado (padrão false).
2. Os seletores de leitura precisam estar homologados (manifesto `validated`).

Sem isso, devolve um status que o chat usa para pedir o texto colado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import Settings, get_settings
from app.sei.read_selector_manifest import (
    evaluate_read_selector_manifest,
    load_read_selector_manifest,
)

DEFAULT_READ_MANIFEST = Path(
    "knowledge_base/sei_homologacao/read_selectors.template.json"
)


@dataclass(frozen=True)
class ReadResult:
    """Resultado da leitura de um processo."""

    status: str  # "ok" | "desabilitado" | "nao_homologado" | "processo_divergente" | "erro"
    texto: str = ""
    titulos: tuple[str, ...] = field(default_factory=tuple)
    motivo: str = ""


def read_current_process(
    numero: str,
    *,
    settings: Settings | None = None,
    manifest_path: str | Path = DEFAULT_READ_MANIFEST,
) -> ReadResult:
    """Lê o processo atualmente aberto e confere o número (somente leitura)."""
    cfg = settings or get_settings()

    if not cfg.enable_sei_browser_automation:
        return ReadResult(
            status="desabilitado",
            motivo="ENABLE_SEI_BROWSER_AUTOMATION=false (padrão seguro).",
        )

    try:
        manifest = load_read_selector_manifest(manifest_path)
        report = evaluate_read_selector_manifest(manifest)
    except Exception as exc:
        return ReadResult(status="nao_homologado", motivo=f"manifesto invalido: {exc}")

    if not report.ok:
        return ReadResult(
            status="nao_homologado",
            motivo="Seletores de leitura ainda não homologados.",
        )

    return _read_with_session(numero, cfg)


def _read_with_session(numero: str, cfg: Settings) -> ReadResult:  # pragma: no cover - requer navegador/SEI
    """Caminho real (gated): abre a sessão efêmera e lê a página atual."""
    from app.sei.playwright_session import open_ephemeral_readonly_session

    try:
        with open_ephemeral_readonly_session(cfg) as page:
            if not page.confirm_process_number(numero):
                visiveis = ", ".join(page.visible_process_numbers()) or "nenhum"
                return ReadResult(
                    status="processo_divergente",
                    motivo=f"Processo aberto não confere com {numero} (visíveis: {visiveis}).",
                )
            titulos = page.document_tree()
            visivel = page.visible_text()
            texto = "\n".join([*titulos, visivel]).strip()
            return ReadResult(status="ok", texto=texto, titulos=titulos)
    except Exception as exc:
        return ReadResult(status="erro", motivo=str(exc) or exc.__class__.__name__)
