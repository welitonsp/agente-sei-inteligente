import os
import pytest
from app.storage.database import init_database
from app.intelligence.learning_policy import register_approved_correction
from app.storage.repositories import list_correcoes_usuario

@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test_agente19.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    from app.core.config import settings
    settings.DATABASE_URL = f"sqlite:///{db_file}"
    init_database()
    return db_file

def test_learning_policy_does_not_save_full_text(temp_db):
    original_text = "texto secreto original"
    corrected_text = "texto secreto corrigido"
    
    metadata = {
        "tipo_documento": "oficio",
        "password": "senha_proibida",
        "full_text": original_text
    }
    
    result = register_approved_correction(original_text, corrected_text, metadata)
    
    # Valida o retorno (Memória)
    assert result["status"] == "correcao_registrada"
    assert "password" not in result["learning_data"]["metadata"]
    assert "full_text" not in result["learning_data"]["metadata"]
    
    # Valida o Banco SQLite (correcoes_usuario)
    correcoes = list_correcoes_usuario()
    assert len(correcoes) == 1
    corr = correcoes[0]
    
    # Hashes salvos, texto não
    assert original_text not in corr.values()
    assert corrected_text not in corr.values()
    assert corr["texto_original_hash"] != ""
