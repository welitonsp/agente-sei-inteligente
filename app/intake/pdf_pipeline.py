import os
import hashlib
import fitz  # PyMuPDF
from app.intake.sanitizer import sanitize_text_preview

def get_file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()

def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def process_pdf_file(pdf_path: str) -> dict:
    if not os.path.exists(pdf_path):
        return {"status": "erro", "reason": "arquivo_nao_encontrado"}
        
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"status": "erro", "reason": f"pdf_invalido: {str(e)}"}
        
    file_hash = get_file_hash(pdf_path)
    
    page_count = doc.page_count
    empty_pages = []
    extracted_text_blocks = []
    
    for page_num in range(page_count):
        page = doc.load_page(page_num)
        text = page.get_text()
        if not text.strip():
            empty_pages.append(page_num)
        extracted_text_blocks.append(text)
        
    extracted_text = "\n".join(extracted_text_blocks)
    total_chars = len(extracted_text)
    
    # Se a média de caracteres por página for muito baixa, provavelmente precisa de OCR
    ocr_required = total_chars < (page_count * 50) and page_count > 0
    
    text_hash = get_text_hash(extracted_text)
    
    safe_preview = sanitize_text_preview(extracted_text)
    
    warnings = []
    if empty_pages:
        warnings.append("Páginas vazias detectadas")
    if ocr_required:
        warnings.append("Documento possivelmente escaneado. OCR pode ser necessário.")
        
    doc.close()
    
    return {
        "status": "sucesso",
        "file_hash": file_hash,
        "text_hash": text_hash,
        "page_count": page_count,
        "total_chars": total_chars,
        "empty_pages": empty_pages,
        "ocr_required": ocr_required,
        "safe_preview": safe_preview,
        "extracted_text": extracted_text, # Mantido apenas para uso em memória, não persistir por padrão
        "warnings": warnings
    }
