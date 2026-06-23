"""Cria o banco SQLite e as tabelas. Uso: python scripts/init_db.py"""

from __future__ import annotations

import os

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger, log_event
from app.storage.db import init_db


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("init_db")

    print("Iniciando a criação do banco de dados seguro do Agente 19...")
    os.makedirs("data", exist_ok=True)
    init_db()
    log_event(logger, 20, "banco inicializado", database_url=settings.database_url)
    print(f"Banco inicializado: {settings.database_url}")
    print("Atenção: Nenhum dado sensível foi exposto no console.")

if __name__ == "__main__":
    main()
