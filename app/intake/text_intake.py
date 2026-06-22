from app.core.audit import get_hash

def receive_manual_text(text: str) -> dict:
    """
    Recebe texto manual, não loga conteúdo integral.
    Retorna hash e quantidade de caracteres.
    """
    text_hash = get_hash(text)
    char_count = len(text)
    
    return {
        "text_hash": text_hash,
        "char_count": char_count,
        "received": True
    }
