"""Resumidor extractivo local e determinístico para documentos administrativos.

Em vez de devolver um texto fixo, seleciona as frases mais relevantes do
documento por pontuação de sinais administrativos (solicitação, prazo, ofício,
despacho, intimação, audiência, etc.) e posição. É 100% offline, sem rede e sem
LLM. A saída passa pelo sanitizador de PII para nunca expor CPF/CNPJ/e-mail/
telefone/número de processo no resumo.
"""

from __future__ import annotations

import re
import unicodedata

from app.intake.sanitizer import sanitize_text_preview

# Sinais que indicam frases com conteúdo decisório/acionável.
_SINAIS: tuple[str, ...] = (
    "solicit", "requer", "requisi", "determin", "intima", "notific",
    "prazo", "oficio", "despacho", "audiencia", "evento", "encaminh",
    "providencia", "decis", "defere", "indefere", "autoriz", "convoc",
    "apuracao", "informa", "responder", "manifest",
)

# Divide frases apenas em pontuação final SEGUIDA de espaço/quebra. Assim não
# fragmenta números como CPF "123.456.789-00" (ponto seguido de dígito).
_RE_FRASE = re.compile(r"(?<=[.!?])\s+")
_RE_ESPACO = re.compile(r"\s+")


def _strip_accents(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _frases(text: str) -> list[str]:
    cruas = _RE_FRASE.split(text)
    return [_RE_ESPACO.sub(" ", f).strip() for f in cruas if f.strip()]


def _pontuar(frase: str, indice: int) -> float:
    base = _strip_accents(frase)
    score = sum(1.0 for sinal in _SINAIS if sinal in base)
    if indice == 0:
        score += 1.5  # a primeira frase costuma trazer o objeto do documento
    if re.search(r"\d", frase):
        score += 0.5  # presença de números (datas, quantidades, prazos)
    return score


def summarize(text: str, *, max_frases: int = 2, max_chars: int = 320) -> str:
    """Gera um resumo extractivo curto e sanitizado.

    Mantém a ordem original das frases selecionadas para preservar a leitura.
    """
    if not text or not text.strip():
        return ""

    frases = _frases(text)
    if not frases:
        return ""
    if len(frases) <= max_frases:
        selecionadas = list(enumerate(frases))
    else:
        pontuadas = sorted(
            enumerate(frases),
            key=lambda par: (_pontuar(par[1], par[0]), -par[0]),
            reverse=True,
        )
        melhores = pontuadas[:max_frases]
        selecionadas = sorted(melhores, key=lambda par: par[0])

    resumo = " ".join(frase for _, frase in selecionadas).strip()
    return sanitize_text_preview(resumo, max_length=max_chars)
