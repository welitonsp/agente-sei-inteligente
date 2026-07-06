"""Sistema de Cache Semântico Idempotente.

Este módulo armazena um hash do texto analisado (ex: o conteúdo de um documento)
e vincula-o ao resumo gerado pelo modelo LLM. Isso evita recálculos caros,
economiza tokens e zera a latência de documentos já lidos no processo.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from typing import Optional


class SemanticCache:
    """Implementa Cache Semântico usando SQLite."""

    def __init__(self, db_path: str = "semantic_cache.db") -> None:
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Inicializa a tabela de cache, se não existir."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS semantic_cache (
                    hash_key TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
            conn.commit()

    def _generate_hash(self, text: str) -> str:
        """Gera um hash SHA-256 para o texto informado."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get_summary(self, text: str) -> Optional[str]:
        """Tenta recuperar o resumo cacheado para o texto dado.
        
        Retorna o resumo se encontrado, ou None se cache-miss.
        """
        if not text:
            return None
            
        hash_key = self._generate_hash(text)
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM semantic_cache WHERE hash_key = ?", (hash_key,))
            row = cursor.fetchone()
            if row:
                return row[0]
        return None

    def set_summary(self, text: str, summary: str) -> None:
        """Salva o resumo no cache vinculado ao hash do texto."""
        if not text or not summary:
            return
            
        hash_key = self._generate_hash(text)
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT OR REPLACE INTO semantic_cache (hash_key, summary)
                VALUES (?, ?)
                ''', (hash_key, summary)
            )
            conn.commit()

# Instância singleton para uso simples em toda a aplicação
cache = SemanticCache()
