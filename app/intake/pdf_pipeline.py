import os

def process_pdf(pdf_path: str) -> dict:
    """
    Stub para receber caminho de PDF, detectar se existe, 
    tentar extrair texto básico. Não salva conteúdo integral em log.
    """
    if not os.path.exists(pdf_path):
        return {"status": "erro", "reason": "arquivo_nao_encontrado"}
        
    return {"status": "ocr_necessario"}
