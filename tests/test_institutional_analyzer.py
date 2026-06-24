from datetime import date

from app.intelligence.institutional_analyzer import analyze_document_rules

def test_analyze_document_rules():
    result = analyze_document_rules("Solicito apoio para ofício e prazo até amanhã")
    assert result["tipo_provavel"] == "oficio"
    assert result["prazo_detectado"] is True
    assert result["evento_detectado"] is False
    assert "providencia_sugerida" in result


def test_analyze_extrai_prazo_estruturado_com_data_limite():
    result = analyze_document_rules(
        "Ofício: responder no prazo de 5 dias.",
        reference_date=date(2026, 6, 24),
    )
    assert result["prazo_detectado"] is True
    assert len(result["prazos"]) == 1
    prazo = result["prazos"][0]
    assert prazo["quantidade"] == 5
    assert prazo["data_limite"] == "2026-06-29"
    # Confiança derivada de sinais (tipo + prazo), não mais fixa em 0.5.
    assert result["confianca"] > 0.5


def test_analyze_resumo_nao_eh_mais_fixo():
    result = analyze_document_rules("Despacho para análise e providências.")
    assert result["resumo_curto"] != "Resumo gerado por regras simples"


def test_analyze_documento_sem_sinais_tem_baixa_confianca():
    result = analyze_document_rules("Texto neutro qualquer.")
    assert result["tipo_provavel"] == "indefinido"
    assert result["confianca"] <= 0.4


def test_deteccao_de_tipo_insensivel_a_acento():
    # "Oficio" sem acento (comum em OCR) deve ser detectado como ofício.
    result = analyze_document_rules("Oficio n. 10/2026 para resposta.")
    assert result["tipo_provavel"] == "oficio"
