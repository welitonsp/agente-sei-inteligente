def register_approved_correction(original_text: str, corrected_text: str, metadata: dict) -> dict:
    """
    Registra correção aprovada para aprendizado supervisionado.
    Garante que não salva senha/cookie/sessão/token.
    """
    safe_metadata = {k: v for k, v in metadata.items() if k not in ["password", "cookie", "token", "session"]}
    
    return {
        "status": "correcao_registrada",
        "learning_data": {
            "original_length": len(original_text),
            "corrected_length": len(corrected_text),
            "metadata": safe_metadata
        }
    }
