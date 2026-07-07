import pytest

from app.storage.database import init_database
from app.storage.repositories import list_unidades_pmgo

@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test_agente19.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    from app.core.config import settings
    settings.DATABASE_URL = f"sqlite:///{db_file}"
    init_database()
    return db_file

def test_seed_19crpm_script(temp_db):
    # Roda o script de seed
    import scripts.seed_19crpm
    scripts.seed_19crpm.main()
    
    unidades = list_unidades_pmgo()
    assert len(unidades) == 5
    siglas = [u["sigla"] for u in unidades]
    assert "19CRPM" in siglas
    assert "OFICIAIS" in siglas
    assert "36BPM" in siglas
    assert "BPTUR" in siglas
    assert "10CIPM" in siglas
