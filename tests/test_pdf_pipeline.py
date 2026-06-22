import os
import fitz
import pytest
from app.intake.pdf_pipeline import process_pdf_file

@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Este é um PDF de teste com CPF 123.456.789-00 para o Agente 19.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_process_pdf_file_extracts_and_sanitizes(dummy_pdf):
    result = process_pdf_file(dummy_pdf)
    
    assert result["status"] == "sucesso"
    assert result["page_count"] == 1
    assert result["total_chars"] > 10
    assert result["ocr_required"] is False
    assert "extracted_text" in result
    assert "123.456.789-00" in result["extracted_text"]
    
    # Valida sanitização na safe_preview
    assert "123.***.***-00" in result["safe_preview"]
    assert "123.456.789-00" not in result["safe_preview"]
    
    # Hashes gerados
    assert result["file_hash"] != ""
    assert result["text_hash"] != ""

def test_process_pdf_missing_file():
    result = process_pdf_file("arquivo_que_nao_existe.pdf")
    assert result["status"] == "erro"
    assert result["reason"] == "arquivo_nao_encontrado"

def test_process_pdf_invalid_file(tmp_path):
    invalid_path = tmp_path / "invalido.pdf"
    invalid_path.write_text("isto não é um pdf")
    result = process_pdf_file(str(invalid_path))
    assert result["status"] == "erro"
    assert "pdf_invalido" in result["reason"]

def test_process_pdf_empty_scanned_pdf(tmp_path):
    # Cria PDF sem texto
    pdf_path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    
    result = process_pdf_file(str(pdf_path))
    assert result["status"] == "sucesso"
    assert result["ocr_required"] is True
    assert result["total_chars"] == 0
    assert len(result["empty_pages"]) > 0
