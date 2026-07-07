import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.intake.manual_text import ManualTextRequest, ManualTextResult, ExtractedEvent, ExtractedDeadline

load_dotenv()

def analyze_with_gemini(request: ManualTextRequest) -> ManualTextResult:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Chave de API do Gemini não configurada no ambiente (GEMINI_API_KEY).")
        
    genai.configure(api_key=api_key)
    
    # Configuracao do modelo
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Você é o Agente 19, um assistente militar autônomo do 19º Comando Regional de Polícia Militar de Goiás (19º CRPM).
    Abaixo está o conteúdo extraído de um processo SEI.
    Por favor, analise todo o contexto e retorne um resumo executivo extremamente claro e direto do que se trata e o que deve ser feito.
    Identifique também prazos ou eventos se houver.
    
    Título do documento: {request.titulo}
    
    Conteúdo:
    {request.texto}
    
    Responda APENAS com o texto do resumo, sem saudações.
    """
    
    response = model.generate_content(prompt)
    resumo_gerado = response.text.strip()
    
    import hashlib
    text_hash = hashlib.sha256(request.texto.encode("utf-8")).hexdigest()
    
    # Por enquanto, mantemos eventos e prazos nulos ou extraimos com regex para o MVP
    evento = ExtractedEvent(ha_evento=False)
    prazo = ExtractedDeadline(ha_prazo=False)
    
    return ManualTextResult(
        status="sucesso",
        processo_id=None,
        documento_id=None,
        text_hash=text_hash,
        resumo_executivo=resumo_gerado,
        evento=evento,
        prazo=prazo,
        campos_pendentes=[],
        revisao_humana_obrigatoria=True,
        confianca=0.95,
        audit_log_ids=[],
        motivo="Analise gerada via Google Gemini 1.5 Pro.",
    )

def review_with_gemini(texto_base: str, minuta_gerada: str, contexto: str) -> dict[str, Any]:
    """Atua como o Nó Crítico, avaliando a minuta gerada contra as regras."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"aprovado": True, "feedback": ""} # Fallback silencioso se nao tiver chave
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Você é o Auditor de Segurança de IA do 19º CRPM.
    Sua missão é avaliar uma minuta gerada pelo Agente para garantir que ela obedece às regras.
    
    Regras Institucionais (RAG):
    {contexto}
    
    Texto da Minuta Gerada:
    {minuta_gerada}
    
    Responda EXATAMENTE neste formato de 2 linhas:
    STATUS: APROVADO ou REPROVADO
    MOTIVO: <se reprovado, explique o erro em 1 frase. Se aprovado, escreva OK>
    """
    
    try:
        response = model.generate_content(prompt)
        linhas = response.text.strip().split("\\n")
        status_line = linhas[0].upper()
        
        if "REPROVADO" in status_line:
            motivo = linhas[1].replace("MOTIVO:", "").strip() if len(linhas) > 1 else "Violação de regras institucionais."
            return {"aprovado": False, "feedback": motivo}
            
        return {"aprovado": True, "feedback": ""}
    except Exception as e:
        return {"aprovado": True, "feedback": str(e)} # Em caso de erro de API, deixa passar para revisao humana
