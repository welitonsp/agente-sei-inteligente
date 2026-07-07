import pytest
from app.storage.database import init_database
from app.storage.repositories import add_unidade_pmgo, list_unidades_pmgo

@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test_agente19.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    from app.core.config import settings
    settings.DATABASE_URL = f"sqlite:///{db_file}"
    init_database()
    return db_file

def test_add_and_list_unidades(temp_db):
    add_unidade_pmgo("TEST", "Unidade Teste", "TIPO", "Cidade", "teste@pm.go.gov.br")
    unidades = list_unidades_pmgo()
    
    assert len(unidades) == 1
    assert unidades[0]["sigla"] == "TEST"
    assert unidades[0]["nome"] == "Unidade Teste"
