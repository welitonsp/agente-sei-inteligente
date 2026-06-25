"""Testes do cérebro do chat do Agente 19 (lógica pura, sem GUI)."""

from __future__ import annotations

from app.desktop.agent_chat import AgentChatController, ChatReply, telegram_summary


def _analise_fake(texto: str) -> dict:
    return {
        "tipo_provavel": "oficio",
        "resumo_curto": "Solicita informações sobre o efetivo.",
        "providencia_sugerida": "Responder Ofício",
        "prazos": [{"descricao": "10 dias úteis", "data_limite": "2026-07-08"}],
    }


def _minuta_fake(payload: dict) -> dict:
    return {"resultado": {"texto": f"Minuta {payload['tipo_minuta']} para {payload['processo_sei']}."}}


def _controller() -> AgentChatController:
    return AgentChatController(analisar=_analise_fake, gerar_minuta=_minuta_fake)


def test_saudacao_menciona_nao_assina():
    r = _controller().saudacao()
    assert isinstance(r, ChatReply)
    assert "não assino" in r.text.lower() or "nao assino" in r.text.lower()


def test_sem_numero_e_sem_conteudo_pede_numero():
    replies = _controller().responder("oi")
    assert len(replies) == 1
    assert "número do processo" in replies[0].text.lower()


def test_numero_sem_conteudo_pede_para_colar():
    replies = _controller().responder("processo 202600000123456")
    assert len(replies) == 1
    assert "cole" in replies[0].text.lower()


def test_fluxo_completo_analisa_e_sugere():
    mensagem = (
        "202600000123456 Ofício solicitando informações sobre o efetivo do 19 CRPM "
        "para apoio, responder no prazo de 10 dias úteis."
    )
    replies = _controller().responder(mensagem)
    texto = "\n".join(r.text for r in replies)

    assert "Tipo provável: oficio" in texto
    assert "10 dias úteis" in texto
    assert "data-limite 2026-07-08" in texto
    assert "Sugiro criar um oficio" in texto
    assert "Minuta oficio para 202600000123456" in texto
    assert "Telegram" in texto
    # Garantia de segurança aparece no fluxo.
    assert "não assino" in texto.lower() or "nao assino" in texto.lower()


def test_telegram_summary_e_curto_e_seguro():
    s = telegram_summary(_analise_fake(""), "202600000123456")
    assert "Agente 19" in s
    assert "Tipo: oficio" in s
    assert "até 2026-07-08" in s
    assert "nao assina" in s.lower()


def test_floating_agent_importa_sem_gui():
    # Import nao deve exigir display (tkinter so e importado dentro da classe/run).
    import app.desktop.floating_agent as fa

    assert callable(fa.run)
    assert hasattr(fa, "FloatingAgentApp")
