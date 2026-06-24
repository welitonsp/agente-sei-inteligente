"""Análise institucional local de documentos (regras + extração offline).

Combina detecção de tipo por palavras-chave, resumo extractivo real e extração
estruturada de prazos. Mantém o contrato histórico de `analyze_document_rules`
(chaves tipo_provavel/resumo_curto/prazo_detectado/evento_detectado/
providencia_sugerida/confianca) e acrescenta `prazos` estruturados e uma
confiança derivada de sinais, em vez de fixa.
"""

from __future__ import annotations

import unicodedata
from datetime import date
from typing import Any, Dict

from app.intelligence.prazo_extractor import Prazo, extract_prazos
from app.intelligence.summarizer import summarize


def _strip_accents(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

KEYWORDS_MAP = {
    "ofício": "oficio",
    "despacho": "despacho",
    "apoio": "apoio",
    "evento": "evento",
    "intimação": "intimacao",
    "requisição": "requisicao",
    "prazo": "prazo",
    "audiência": "audiencia",
    "ordem de atendimento": "ordem_de_atendimento",
}

_PROVIDENCIA_POR_TIPO = {
    "oficio": "Responder Ofício",
    "despacho": "Analisar Despacho e prosseguir",
    "intimacao": "Cumprir intimação dentro do prazo",
    "requisicao": "Atender requisição e responder",
    "audiencia": "Preparar e registrar a audiência na agenda",
    "evento": "Registrar evento na agenda",
}


def _prazo_to_dict(p: Prazo) -> Dict[str, Any]:
    return {
        "tipo": p.tipo,
        "descricao": p.descricao(),
        "quantidade": p.quantidade,
        "unidade": p.unidade,
        "dias_uteis": p.dias_uteis,
        "data_limite": p.data_limite.isoformat() if p.data_limite else None,
    }


def analyze_document_rules(
    text: str, *, reference_date: date | None = None
) -> Dict[str, Any]:
    # Match insensível a acento: documentos reais/OCR do SEI muitas vezes vêm
    # sem acentuação ("Oficio", "intimacao"). Comparamos formas normalizadas.
    text_norm = _strip_accents(text)
    detectado = [
        tipo for kw, tipo in KEYWORDS_MAP.items() if _strip_accents(kw) in text_norm
    ]
    tipo_provavel = detectado[0] if detectado else "indefinido"

    prazos = extract_prazos(text, reference_date=reference_date)
    tem_prazo = bool(prazos) or "prazo" in detectado
    tem_evento = "evento" in detectado or "audiencia" in detectado

    providencia_sugerida = _PROVIDENCIA_POR_TIPO.get(
        tipo_provavel, "Analisar e elaborar resposta"
    )
    if prazos:
        prazo_desc = prazos[0].descricao()
        providencia_sugerida += f" (atentar ao prazo: {prazo_desc})"

    # Confiança derivada de sinais, em vez de fixa.
    confianca = 0.3
    if tipo_provavel != "indefinido":
        confianca += 0.3
    if prazos:
        confianca += 0.2
    if tem_evento:
        confianca += 0.1
    if len(detectado) >= 2:
        confianca += 0.1
    confianca = round(min(confianca, 0.9), 2)

    return {
        "tipo_provavel": tipo_provavel,
        "tipos_detectados": detectado,
        "resumo_curto": summarize(text) or "Sem conteúdo textual para resumir.",
        "prazo_detectado": tem_prazo,
        "prazos": [_prazo_to_dict(p) for p in prazos],
        "evento_detectado": tem_evento,
        "providencia_sugerida": providencia_sugerida,
        "confianca": confianca,
    }


def analyze_pdf_pipeline_result(
    result: Dict[str, Any], *, reference_date: date | None = None
) -> Dict[str, Any]:
    if result.get("status") != "sucesso":
        return {
            "status": "erro",
            "motivo": result.get("reason", "Erro desconhecido no pipeline PDF"),
        }

    if result.get("ocr_required"):
        return {
            "tipo_provavel": "indefinido_documento_escaneado",
            "resumo_curto": "Documento requer OCR ou leitura humana (imagem).",
            "prazo_detectado": False,
            "prazos": [],
            "evento_detectado": False,
            "providencia_sugerida": "Realizar leitura humana ou aplicar pipeline de OCR futuramente.",
            "confianca": 1.0,
            "seguranca": "Nenhum texto integral extraido pelo analisador.",
        }

    extracted_text = result.get("extracted_text", "")
    analysis = analyze_document_rules(extracted_text, reference_date=reference_date)

    analysis["hashes"] = {"text_hash": result.get("text_hash")}
    analysis["safe_preview"] = result.get("safe_preview")

    return analysis
