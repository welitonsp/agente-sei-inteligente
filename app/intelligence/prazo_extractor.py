"""Extrator local e determinístico de prazos em textos administrativos (SEI).

Identifica prazos relativos ("no prazo de 10 (dez) dias úteis", "em 48 horas")
e absolutos ("até 30/06/2026", "até o dia 30 de junho de 2026"). Opera 100%
offline, sem rede e sem LLM, coerente com a premissa de leitura supervisionada
e custo zero. Não extrai nem expõe texto integral: devolve apenas o trecho do
prazo e os campos estruturados.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

# Números por extenso comuns em prazos administrativos.
_NUMEROS_EXTENSO: dict[str, int] = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4,
    "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
    "quinze": 15, "vinte": 20, "trinta": 30, "quarenta": 40, "sessenta": 60,
    "noventa": 90,
}

_MESES: dict[str, int] = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}

# "no prazo de 10 (dez) dias úteis", "em 5 dias", "prazo de 48 horas".
_RE_RELATIVO = re.compile(
    r"(?:no\s+prazo\s+de|dentro\s+de|em|prazo\s+de|prazo\s+m[aá]ximo\s+de)\s+"
    r"(\d{1,3}|[a-zçãéê]+)\s*"
    r"(?:\([^)]*\)\s*)?"
    r"(dias?|horas?)"
    r"(\s+[uú]teis|\s+corridos)?",
    re.IGNORECASE,
)

# "até 30/06/2026" ou "até o dia 30/06/2026".
_RE_ABSOLUTO_NUM = re.compile(
    r"at[eé]\s+(?:o\s+dia\s+)?(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})",
    re.IGNORECASE,
)

# "até 30 de junho de 2026".
_RE_ABSOLUTO_EXTENSO = re.compile(
    r"at[eé]\s+(?:o\s+dia\s+)?(\d{1,2})\s+de\s+([a-zçã]+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Prazo:
    """Prazo estruturado extraído de um texto."""

    tipo: str  # "relativo" | "absoluto"
    trecho: str
    quantidade: int | None = None
    unidade: str | None = None  # "dias" | "horas"
    dias_uteis: bool = False
    data_limite: date | None = None

    def descricao(self) -> str:
        if self.tipo == "absoluto" and self.data_limite:
            return f"até {self.data_limite.strftime('%d/%m/%Y')}"
        if self.quantidade is not None:
            sufixo = " úteis" if self.dias_uteis else ""
            return f"{self.quantidade} {self.unidade}{sufixo}"
        return self.trecho


def _strip_accents(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _parse_quantidade(token: str) -> int | None:
    token = token.strip()
    if token.isdigit():
        return int(token)
    return _NUMEROS_EXTENSO.get(_strip_accents(token))


def _add_business_days(start: date, days: int) -> date:
    """Soma dias úteis (aproximação: pula sábados e domingos; sem feriados)."""
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:  # 0=segunda ... 4=sexta
            remaining -= 1
    return current


def extract_prazos(text: str, *, reference_date: date | None = None) -> list[Prazo]:
    """Extrai prazos de um texto. `reference_date` permite calcular a data-limite
    de prazos relativos (ex.: "5 dias" a partir de hoje)."""
    if not text:
        return []

    prazos: list[Prazo] = []

    for m in _RE_RELATIVO.finditer(text):
        quantidade = _parse_quantidade(m.group(1))
        if quantidade is None:
            continue
        unidade_raw = _strip_accents(m.group(2))
        unidade = "horas" if unidade_raw.startswith("hora") else "dias"
        dias_uteis = "uteis" in _strip_accents(m.group(3) or "")
        data_limite: date | None = None
        if reference_date is not None and unidade == "dias":
            data_limite = (
                _add_business_days(reference_date, quantidade)
                if dias_uteis
                else reference_date + timedelta(days=quantidade)
            )
        prazos.append(
            Prazo(
                tipo="relativo",
                trecho=m.group(0).strip(),
                quantidade=quantidade,
                unidade=unidade,
                dias_uteis=dias_uteis,
                data_limite=data_limite,
            )
        )

    for m in _RE_ABSOLUTO_NUM.finditer(text):
        dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if ano < 100:
            ano += 2000
        data_limite = _safe_date(ano, mes, dia)
        if data_limite is None:
            continue
        prazos.append(Prazo(tipo="absoluto", trecho=m.group(0).strip(), data_limite=data_limite))

    for m in _RE_ABSOLUTO_EXTENSO.finditer(text):
        dia, mes_nome, ano = int(m.group(1)), _strip_accents(m.group(2)), int(m.group(3))
        mes_num = _MESES.get(mes_nome)
        if mes_num is None:
            continue
        data_limite = _safe_date(ano, mes_num, dia)
        if data_limite is None:
            continue
        prazos.append(Prazo(tipo="absoluto", trecho=m.group(0).strip(), data_limite=data_limite))

    return _dedupe(prazos)


def _safe_date(ano: int, mes: int, dia: int) -> date | None:
    try:
        return date(ano, mes, dia)
    except ValueError:
        return None


def _dedupe(prazos: list[Prazo]) -> list[Prazo]:
    seen: set[tuple] = set()
    unicos: list[Prazo] = []
    for p in prazos:
        chave = (p.tipo, p.quantidade, p.unidade, p.dias_uteis, p.data_limite)
        if chave not in seen:
            seen.add(chave)
            unicos.append(p)
    return unicos
