from app.intelligence.institutional_analyzer import analyze_document_rules

def test_analyze_document_rules():
    result = analyze_document_rules("Solicito apoio para ofício e prazo até amanhã")
    assert result["tipo_provavel"] == "oficio"
    assert result["prazo_detectado"] is True
    assert result["evento_detectado"] is False
    assert "providencia_sugerida" in result
