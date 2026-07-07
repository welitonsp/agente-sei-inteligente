"""Testes da ligação leitura->chat (Frente 2, gated)."""

from __future__ import annotations

from app.core.config import Settings
from app.desktop.agent_chat import AgentChatController
from app.sei.process_reader import ReadResult, read_current_process


# --- Portões do leitor (sem navegador) ---------------------------------------

def test_leitor_desabilitado_quando_flag_off():
    r = read_current_process("202600000123456", settings=Settings(enable_sei_browser_automation=False))
    assert r.status == "desabilitado"


def test_leitor_nao_homologado_quando_manifesto_pending(tmp_path):
    # Flag ligada, mas um manifesto 'pending' -> nao_homologado (sem abrir navegador).
    import json

    pend = tmp_path / "pending.json"
    pend.write_text(
        json.dumps(
            {
                "version": "x",
                "selectors": {
                    "tree_frame": {"value": "ifrArvore", "status": "pending"},
                    "content_frame": {"value": "ifrVisualizacao", "status": "pending"},
                },
            }
        ),
        encoding="utf-8",
    )
    r = read_current_process(
        "202600000123456",
        settings=Settings(enable_sei_browser_automation=True),
        manifest_path=pend,
    )
    assert r.status == "nao_homologado"


# --- Chat usando o leitor (injetado) -----------------------------------------

def _analise_fake(texto: str) -> dict:
    return {"tipo_provavel": "despacho", "resumo_curto": "ok", "providencia_sugerida": "Analisar", "prazos": []}


def _minuta_fake(payload: dict) -> dict:
    return {"resultado": {"texto": "rascunho"}}


def test_chat_le_automaticamente_quando_leitor_ok():
    def leitor(n): return ReadResult(status="ok", texto="Despacho para analise no processo.", titulos=("Doc 1",))
    ctrl = AgentChatController(analisar=_analise_fake, gerar_minuta=_minuta_fake, ler_processo=leitor)
    replies = ctrl.responder("202600000123456")
    texto = "\n".join(r.text for r in replies)
    assert "Li o processo 202600000123456" in texto
    assert "Tipo provável: despacho" in texto


def test_chat_pede_colar_quando_leitor_desabilitado():
    def leitor(n): return ReadResult(status="desabilitado", motivo="flag off")
    ctrl = AgentChatController(analisar=_analise_fake, gerar_minuta=_minuta_fake, ler_processo=leitor)
    replies = ctrl.responder("202600000123456")
    assert len(replies) == 1
    assert "desligada" in replies[0].text.lower()
    assert "cole" in replies[0].text.lower()


def test_chat_avisa_processo_divergente():
    def leitor(n): return ReadResult(status="processo_divergente", motivo="nao confere")
    ctrl = AgentChatController(analisar=_analise_fake, gerar_minuta=_minuta_fake, ler_processo=leitor)
    replies = ctrl.responder("202600000123456")
    assert "não confere" in replies[0].text.lower() or "nao confere" in replies[0].text.lower()


def test_chat_sem_leitor_mantem_pedido_de_colar():
    ctrl = AgentChatController(analisar=_analise_fake, gerar_minuta=_minuta_fake)
    replies = ctrl.responder("202600000123456")
    assert "cole" in replies[0].text.lower()
