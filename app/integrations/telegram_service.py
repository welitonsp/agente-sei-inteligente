"""Serviço de alertas via Telegram (canal operacional inicial — docs/05, docs/12).

Princípios do projeto respeitados:

- **Custo/dependência zero**: o backend real usa `urllib` da biblioteca padrão;
  não há SDK pago nem pacote novo.
- **Inerte até autorização**: sem `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` no
  `.env`, a fábrica devolve o backend *dry-run* (não envia nada). Isso respeita a
  pergunta em aberto de docs/13 sobre a autorização do canal.
- **Nunca vaza documento**: a mensagem é montada apenas com campos curtos
  (tipo, título, resumo truncado, prazo, unidade). O número do processo é
  mascarado; texto integral nunca entra no alerta (docs/05, docs/25).
- **Auditoria resiliente**: cada envio é auditado; falha de auditoria nunca
  impede a entrega do alerta.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from app.core import audit
from app.core.config import Settings, get_settings

_logger = logging.getLogger("agente19.telegram")

# Limite conservador do resumo no alerta: garante que nunca enviamos documento.
_RESUMO_MAX = 280


class AlertType(str, Enum):
    PRAZO = "prazo"
    EVENTO = "evento"
    MINUTA = "minuta"
    ERRO = "erro"
    INFO = "info"


_ICON = {
    AlertType.PRAZO: "⏰",  # relógio
    AlertType.EVENTO: "\U0001f4c5",  # calendário
    AlertType.MINUTA: "\U0001f4dd",  # papel
    AlertType.ERRO: "⚠️",  # aviso
    AlertType.INFO: "ℹ️",  # info
}


@dataclass(frozen=True)
class Alert:
    tipo: AlertType
    titulo: str
    resumo: str = ""
    processo_sei: str = ""
    prazo: str = ""
    unidade: str = ""
    origem: str = "agente19"


@dataclass(frozen=True)
class AlertResult:
    status: str  # sent | simulated | erro
    message_id: str = ""
    texto: str = ""
    motivo: str = ""


def build_message(alert: Alert) -> str:
    """Monta a mensagem padronizada e SEGURA (sem documento integral)."""
    icon = _ICON.get(alert.tipo, "")
    linhas = [f"{icon} Agente 19 — {alert.tipo.value.upper()}".strip()]
    if alert.titulo.strip():
        linhas.append(f"Assunto: {alert.titulo.strip()}")
    if alert.processo_sei.strip():
        linhas.append(f"Processo: {audit.mask_process_number(alert.processo_sei.strip())}")
    if alert.unidade.strip():
        linhas.append(f"Unidade: {alert.unidade.strip()}")
    if alert.prazo.strip():
        linhas.append(f"Prazo: {alert.prazo.strip()}")
    if alert.resumo.strip():
        resumo = " ".join(alert.resumo.split())
        if len(resumo) > _RESUMO_MAX:
            resumo = resumo[: _RESUMO_MAX - 1].rstrip() + "…"
        linhas.append(f"Resumo: {resumo}")
    linhas.append("— Revisão humana obrigatória. Atos oficiais no SEI são manuais.")
    return "\n".join(linhas)


class TelegramBackend(Protocol):
    def send(self, chat_id: str, text: str) -> str:
        """Envia a mensagem e devolve o id. Levanta em caso de falha."""
        ...

    @property
    def is_real(self) -> bool:
        ...


class DryRunTelegramBackend:
    """Backend de simulação: guarda mensagens em memória, sem rede."""

    is_real = False

    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send(self, chat_id: str, text: str) -> str:
        self.sent.append({"chat_id": chat_id, "text": text})
        return f"dry-run-{len(self.sent)}"


class HttpTelegramBackend:
    """Backend real via Bot API, usando apenas a biblioteca padrão."""

    is_real = True

    def __init__(self, token: str, *, timeout: float = 10.0) -> None:
        self._token = token
        self._timeout = timeout

    def send(self, chat_id: str, text: str) -> str:
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        data = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}
        ).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram recusou o envio: {payload}")
        return str(payload.get("result", {}).get("message_id", ""))


def get_telegram_backend(settings: Settings | None = None) -> TelegramBackend:
    """Fábrica: backend real só quando há token; caso contrário, dry-run."""
    cfg = settings or get_settings()
    token = (cfg.telegram_bot_token or "").strip()
    if token:
        return HttpTelegramBackend(token)
    return DryRunTelegramBackend()


def send_alert(
    alert: Alert,
    *,
    backend: TelegramBackend | None = None,
    chat_id: str = "",
    usuario_local: str = "",
    settings: Settings | None = None,
) -> AlertResult:
    """Monta, envia (ou simula) e audita um alerta. Nunca envia documento."""
    cfg = settings or get_settings()
    backend = backend or get_telegram_backend(cfg)
    destino = (chat_id or cfg.telegram_chat_id or "").strip()
    texto = build_message(alert)

    if backend.is_real and not destino:
        return _audited(
            AlertResult(
                status="erro",
                texto=texto,
                motivo="TELEGRAM_CHAT_ID ausente; alerta não enviado.",
            ),
            alert,
            usuario_local,
        )

    try:
        message_id = backend.send(destino, texto)
    except Exception as exc:  # falha de rede/token não deve derrubar o fluxo
        _logger.warning("Falha ao enviar alerta Telegram: %s", exc)
        return _audited(
            AlertResult(status="erro", texto=texto, motivo=str(exc)),
            alert,
            usuario_local,
        )

    status = "sent" if backend.is_real else "simulated"
    return _audited(
        AlertResult(status=status, message_id=message_id, texto=texto),
        alert,
        usuario_local,
    )


def _audited(result: AlertResult, alert: Alert, usuario_local: str) -> AlertResult:
    """Registra auditoria sem nunca bloquear a entrega do alerta."""
    try:
        audit.record(
            action="ENVIAR_ALERTA_TELEGRAM",
            result=result.status,
            actor_id=usuario_local or None,
            target_type="processo_sei",
            target_id=alert.processo_sei or None,
            reason=result.motivo or f"Alerta {alert.tipo.value} processado.",
            metadata={
                "tipo": alert.tipo.value,
                "origem": alert.origem,
                "message_id": result.message_id,
                "texto_integral_persistido": False,
            },
        )
    except Exception as exc:  # auditoria é secundária ao alerta
        _logger.warning("Alerta enviado, mas auditoria falhou: %s", exc)
    return result


def notify_deadline(
    *,
    titulo: str,
    prazo: str,
    processo_sei: str = "",
    unidade: str = "",
    resumo: str = "",
    usuario_local: str = "",
    backend: TelegramBackend | None = None,
) -> AlertResult:
    """Atalho para o caso de uso mais comum: alerta de prazo."""
    return send_alert(
        Alert(
            tipo=AlertType.PRAZO,
            titulo=titulo,
            resumo=resumo,
            processo_sei=processo_sei,
            prazo=prazo,
            unidade=unidade,
        ),
        backend=backend,
        usuario_local=usuario_local,
    )


__all__ = [
    "Alert",
    "AlertResult",
    "AlertType",
    "DryRunTelegramBackend",
    "HttpTelegramBackend",
    "build_message",
    "get_telegram_backend",
    "notify_deadline",
    "send_alert",
]
