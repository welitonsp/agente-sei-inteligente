def generate_draft(draft_type: str, context: dict) -> dict:
    """
    Gera texto inicial de minuta apenas em memória.
    """
    valid_types = ["oficio", "despacho", "ordem_de_atendimento"]
    if draft_type not in valid_types:
        raise ValueError(f"Tipo de minuta inválido: {draft_type}")
        
    draft_content = f"Minuta padrão para {draft_type}.\n\nContexto: {context.get('assunto', 'Sem assunto')}"
    
    return {
        "draft_type": draft_type,
        "content": draft_content,
        "status": "minuta_gerada_para_revisao"
    }
