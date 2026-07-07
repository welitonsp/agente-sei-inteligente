import os
import sqlite3
from app.storage.database import init_database

def test_database_initialization(monkeypatch, tmp_path):
    # Usar um banco temporário para o teste
    db_file = tmp_path / "test_agente19.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    from app.core.config import settings
    settings.DATABASE_URL = f"sqlite:///{db_file}"
    
    init_database()
    
    assert os.path.exists(db_file)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "unidades_pmgo" in tables
    assert "modelos_aprovados" in tables
    assert "correcoes_usuario" in tables
    assert "decisoes_validadas" in tables
    assert "regras_aprendizado" in tables
    assert "auditoria_eventos" in tables
    
    conn.close()
