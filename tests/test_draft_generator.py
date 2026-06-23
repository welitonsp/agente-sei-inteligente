import pytest
from app.intelligence.draft_generator import generate_draft

def test_generate_draft_valid_type():
    result = generate_draft("oficio", {"assunto": "Teste"})
    assert result["status"] == "minuta_gerada_para_revisao"
    assert "minuta padrão" in result["content"].lower()

def test_generate_draft_invalid_type():
    with pytest.raises(ValueError):
        generate_draft("tipo_invalido", {})
