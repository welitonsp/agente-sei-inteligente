"""Camada de banco de dados (SQLite no MVP, preparada para PostgreSQL).

Usa SQLAlchemy 2.0. A troca para PostgreSQL exige apenas mudar DATABASE_URL.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa de todos os modelos."""


_settings = get_settings()

# check_same_thread=False permite uso em apps web; connect_args so vale p/ sqlite.
_connect_args = (
    {"check_same_thread": False}
    if _settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    _settings.database_url,
    echo=False,
    future=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Cria as tabelas que ainda nao existem."""
    # Import tardio garante que os modelos sejam registrados em Base.metadata.
    from app.storage import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Sessao transacional: commit no sucesso, rollback no erro."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
