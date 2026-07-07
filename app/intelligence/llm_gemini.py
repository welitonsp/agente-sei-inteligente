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
