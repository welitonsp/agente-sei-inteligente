from app.storage.repositories import add_correcao_usuario, add_decisao_validada
from app.core.audit import get_hash

def register_approved_correction(original_text: str, corrected_text: str, metadata: dict) -> dict:
    """
    Registra correção aprovada para aprendizado supervisionado.
    Garante que não salva senha/cookie/sessão/token nem o texto integral.
    """
    safe_metadata = {k: v for k, v in metadata.items() if k not in ["password", "cookie", "token", "session", "full_text"]}
    
    # Hash dos textos originais e corrigidos (não salva texto em claro para segurança)
    orig_hash = get_hash(original_text)
    corr_hash = get_hash(corrected_text)
    
    tipo_documento = metadata.get("tipo_documento", "indefinido")
    resumo_correcao = metadata.get("resumo_correcao", "Correção geral de minuta")
    aprovado_por = metadata.get("aprovado_por", "servidor_anonimo")
    
    # Salvar no banco
    add_correcao_usuario(tipo_documento, orig_hash, corr_hash, resumo_correcao, aprovado_por)
    
    return {
        "status": "correcao_registrada",
        "learning_data": {
            "original_hash": orig_hash,
            "corrected_hash": corr_hash,
            "original_length": len(original_text),
            "corrected_length": len(corrected_text),
            "metadata": safe_metadata
        }
    }

def register_validated_decision(tipo_processo: str, assunto_detectado: str, documento_escolhido: str, providencia_aprovada: str, confianca: float, aprovado_por: str) -> dict:
    add_decisao_validada(tipo_processo, assunto_detectado, documento_escolhido, providencia_aprovada, confianca, aprovado_por)
    return {"status": "decisao_validada_registrada"}
