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

    selectors = manifest.get("selectors", {})
    tree_frame = str(selectors.get("tree_frame", {}).get("value", "")).strip()
    content_frame = str(selectors.get("content_frame", {}).get("value", "")).strip()
    return _read_with_session(numero, cfg, tree_frame, content_frame)


def _digits(value: str) -> str:
    return "".join(c for c in str(value) if c.isdigit())


def _confere_numero(numero: str, titulos: tuple[str, ...]) -> bool:
    alvo = _digits(numero)
    if not alvo:
        return False
    return alvo in _digits(" ".join(titulos))


def _read_with_session(  # pragma: no cover - requer navegador/SEI
    numero: str, cfg: Settings, tree_frame: str, content_frame: str
) -> ReadResult:
    """Caminho real (gated): abre a sessão efêmera e lê os frames do processo."""
    from app.sei.playwright_session import open_ephemeral_readonly_session

    try:
        with open_ephemeral_readonly_session(cfg) as page:
            titulos = page.frame_links(tree_frame) if tree_frame else ()
            if not _confere_numero(numero, titulos):
                visiveis = ", ".join(page.visible_process_numbers()) or "nenhum"
                return ReadResult(
                    status="processo_divergente",
                    motivo=(
                        f"Não encontrei o processo {numero} na árvore aberta. "
                        f"Abra esse processo no SEI. (visíveis na caixa: {visiveis})"
                    ),
                )
            conteudo = page.frame_text(content_frame) if content_frame else ""
            # Remove o próprio número/cabeçalho repetido para um texto mais limpo.
            docs = tuple(t for t in titulos if _digits(t) != _digits(numero))
            texto = "\n".join([*docs, conteudo]).strip()
            return ReadResult(status="ok", texto=texto, titulos=docs)
    except Exception as exc:
        return ReadResult(status="erro", motivo=str(exc) or exc.__class__.__name__)
