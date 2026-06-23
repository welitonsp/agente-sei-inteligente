"""Logger estruturado do agente.

Emite logs em JSON por linha (uma linha = um evento), com sanitizacao
automatica de campos sensiveis. Nivel configurado por LOG_LEVEL.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.security_filter import sanitize


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "context", None)
        if isinstance(extra, dict):
            payload["context"] = sanitize(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


_configured = False


def configure_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger("agente_sei")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    root.propagate = False
    _configured = True


def get_logger(name: str = "agente_sei") -> logging.Logger:
    if not _configured:
        configure_logging()
    if name == "agente_sei":
        return logging.getLogger("agente_sei")
    return logging.getLogger(f"agente_sei.{name}")


def log_event(logger: logging.Logger, level: int, message: str, **context: Any) -> None:
    """Loga um evento com contexto estruturado (sanitizado automaticamente)."""
    logger.log(level, message, extra={"context": context})
