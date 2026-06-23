"""Modelos de dados do agente (docs/11-modelo-de-dados.md).

Entidades: processes, documents, emails, events, drafts, notifications,
audit_logs, settings.

Importante: por padrao o sistema guarda metadados, hash, resumo e resultado
estruturado, evitando texto integral de documento do SEI (docs/25).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )


class Process(TimestampMixin, Base):
    __tablename__ = "processes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sei_number: Mapped[str | None] = mapped_column(String(120), index=True)
    subject: Mapped[str | None] = mapped_column(String(500))
    origin: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="recebida")


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int | None] = mapped_column(ForeignKey("processes.id"))
    source_type: Mapped[str] = mapped_column(String(50))  # email|pdf|texto|sei
    source_reference: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(String(500))
    text_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    extracted_text_path: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    classification: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float | None] = mapped_column()


class Email(TimestampMixin, Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sender: Mapped[str | None] = mapped_column(String(255))
    recipients: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(500))
    received_at: Mapped[datetime | None] = mapped_column(DateTime)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="recebida")
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_reference: Mapped[str | None] = mapped_column(String(500))


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int | None] = mapped_column(ForeignKey("processes.id"))
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))
    title: Mapped[str] = mapped_column(String(500))
    event_type: Mapped[str | None] = mapped_column(String(50))
    start_at: Mapped[datetime | None] = mapped_column(DateTime)
    end_at: Mapped[datetime | None] = mapped_column(DateTime)
    location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    deduplication_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    google_event_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pendente")


class Draft(TimestampMixin, Base):
    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int | None] = mapped_column(ForeignKey("processes.id"))
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))
    draft_type: Mapped[str] = mapped_column(String(100))
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="rascunho")
    reviewed_by: Mapped[str | None] = mapped_column(String(255))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    related_type: Mapped[str | None] = mapped_column(String(50))
    related_id: Mapped[int | None] = mapped_column(Integer)
    channel: Mapped[str] = mapped_column(String(50))
    recipient: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="informativo")
    status: Mapped[str] = mapped_column(String(50), default="pendente")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_type: Mapped[str] = mapped_column(String(50))  # agente|usuario|sistema
    actor_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100), index=True)
    target_type: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str] = mapped_column(String(50))  # permitido|bloqueado|...
    reason: Mapped[str | None] = mapped_column(Text)
    # Atributo Python 'meta_json' mapeado para a coluna 'metadata' (sanitizada).
    meta_json: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    value: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(500))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

import sqlite3

def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unidades_pmgo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT,
            nome TEXT,
            tipo_unidade TEXT,
            municipio TEXT,
            email_institucional TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos_aprovados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT,
            titulo TEXT,
            conteudo_template TEXT,
            origem TEXT,
            aprovado_por TEXT,
            versao TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correcoes_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT,
            texto_original_hash TEXT,
            texto_corrigido_hash TEXT,
            resumo_correcao TEXT,
            aprovado_por TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisoes_validadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_processo TEXT,
            assunto_detectado TEXT,
            documento_escolhido TEXT,
            providencia_aprovada TEXT,
            confianca REAL,
            aprovado_por TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regras_aprendizado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            condicao TEXT,
            acao_sugerida TEXT,
            confianca_base REAL,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            process_number_masked TEXT,
            process_number_hash TEXT,
            action TEXT,
            status TEXT,
            metadata_json TEXT
        )
    """)
    
    conn.commit()

