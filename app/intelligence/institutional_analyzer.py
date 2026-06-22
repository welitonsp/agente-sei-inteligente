from typing import Dict, Any

KEYWORDS_MAP = {
    "ofício": "oficio",
    "despacho": "despacho",
    "apoio": "apoio",
    "evento": "evento",
    "intimação": "intimacao",
    "requisição": "requisicao",
    "prazo": "prazo",
    "audiência": "audiencia",
    "ordem de atendimento": "ordem_de_atendimento"
}

def analyze_document_rules(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    detectado = []
    for kw, tipo in KEYWORDS_MAP.items():
        if kw in text_lower:
            detectado.append(tipo)
            
    tipo_provavel = detectado[0] if detectado else "indefinido"
    
    tem_prazo = "prazo" in detectado
    tem_evento = "evento" in detectado or "audiencia" in detectado
    
    providencia_sugerida = "Analisar e elaborar resposta"
    if tipo_provavel == "oficio":
        providencia_sugerida = "Responder Ofício"
    elif tipo_provavel == "despacho":
        providencia_sugerida = "Analisar Despacho e prosseguir"
        
    return {
        "tipo_provavel": tipo_provavel,
        "resumo_curto": "Resumo gerado por regras simples",
        "prazo_detectado": tem_prazo,
        "evento_detectado": tem_evento,
        "providencia_sugerida": providencia_sugerida,
        "confianca": 0.5 
    }
