"""Testes do serviço de alertas Telegram (dry-run por padrão, sem rede)."""

from __future__ import annotations

from app.core.config import Settings
from app.integrations.telegram_service import (
    Alert,
    AlertType,
    DryRunTelegramBackend,
    HttpTelegramBackend,
    build_message,
    get_telegram_backend,
    notify_deadline,
    send_alert,
)


class _FakeBackend:
    """Backend 'real' controlável para testar o caminho de envio."""

    is_real = True

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def send(self, chat_id: str, text: str) -> str:
        self.calls.append((chat_id, text))
        return "42"


class _BoomBackend:
    is_real = True

    def send(self, chat_id: str, text: str) -> str:
        raise RuntimeError("rede caiu")


# --- build_message -----------------------------------------------------------


def test_mensagem_mascara_processo_e_nao_vaza_texto():
    alert = Alert(
        tipo=AlertType.PRAZO,
        titulo="Responder ofício",
        resumo="x" * 5000,  # tenta vazar documento inteiro
        processo_sei="202400123456",
        prazo="2026-07-15",
        unidade="PM/19 CRPM",
    )
    texto = build_message(alert)
    assert "PRAZO" in texto
    assert "202400123456" not in texto  # numero mascarado
    assert "202***456" in texto
    assert "Revisão humana obrigatória" in texto
    assert len(texto) < 600  # resumo truncado, sem documento integral


def test_mensagem_omite_campos_vazios():
    texto = build_message(Alert(tipo=AlertType.INFO, titulo="Só título"))
    assert "Processo:" not in texto
    assert "Prazo:" not in texto


# --- fábrica -----------------------------------------------------------------


def test_fabrica_sem_token_e_dry_run():
    backend = get_telegram_backend(Settings(telegram_bot_token=""))
    assert isinstance(backend, DryRunTelegramBackend)
    assert backend.is_real is False


def test_fabrica_com_token_e_real():
    backend = get_telegram_backend(Settings(telegram_bot_token="123:abc"))
    assert isinstance(backend, HttpTelegramBackend)
    assert backend.is_real is True


# --- send_alert --------------------------------------------------------------


def test_dry_run_simula_e_guarda_mensagem():
    backend = DryRunTelegramBackend()
    r = send_alert(
        Alert(tipo=AlertType.EVENTO, titulo="Reunião"),
        backend=backend,
        chat_id="chat-1",
    )
    assert r.status == "simulated"
    assert len(backend.sent) == 1
    assert backend.sent[0]["chat_id"] == "chat-1"


def test_envio_real_com_backend_injetado():
    backend = _FakeBackend()
    r = send_alert(
        Alert(tipo=AlertType.PRAZO, titulo="Prazo"),
        backend=backend,
        chat_id="chat-9",
    )
    assert r.status == "sent"
    assert r.message_id == "42"
    assert backend.calls[0][0] == "chat-9"


def test_real_sem_chat_id_retorna_erro_sem_enviar():
    backend = _FakeBackend()
    r = send_alert(
        Alert(tipo=AlertType.PRAZO, titulo="Prazo"),
        backend=backend,
        chat_id="",
        settings=Settings(telegram_chat_id=""),
    )
    assert r.status == "erro"
    assert backend.calls == []  # nao tentou enviar


def test_falha_de_envio_nao_propaga():
    r = send_alert(
        Alert(tipo=AlertType.ERRO, titulo="Falha"),
        backend=_BoomBackend(),
        chat_id="chat-x",
    )
    assert r.status == "erro"
    assert "rede caiu" in r.motivo


def test_notify_deadline_atalho():
    backend = DryRunTelegramBackend()
    r = notify_deadline(
        titulo="Intimação",
        prazo="2026-07-20",
        processo_sei="202400999888",
        backend=backend,
    )
    assert r.status == "simulated"
    assert "Prazo: 2026-07-20" in backend.sent[0]["text"]
