import subprocess
import os
import fitz
import pytest

@pytest.fixture
def test_pdf(tmp_path):
    pdf_path = tmp_path / "test_doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Ofício de intimação. CPF 123.456.789-00 Prazo de 5 dias.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_analyze_pdf_script(test_pdf):
    script_path = os.path.join("scripts", "analyze_pdf.py")
    
    # Adicionamos a VENV atual se disponível para rodar o subprocess
    python_exec = "python"
    if os.path.exists(".venv/Scripts/python.exe"):
        python_exec = ".venv/Scripts/python.exe"
        
    result = subprocess.run(
        [python_exec, script_path, test_pdf],
        capture_output=True, text=True
    )
    
    output = result.stdout
    
    assert result.returncode == 0
    assert "Resultado da Análise Institucional" in output
    assert "Tipo Provável: oficio" in output
    assert "123.***.***-00" in output # Sanitizado
    assert "123.456.789-00" not in output # Nao pode vazar real no log
    assert "Texto bruto expurgado" in output
