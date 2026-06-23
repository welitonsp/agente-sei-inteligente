"""Leitor read-only de agenda via feed iCal (ICS) privado do Google.

Util para LER eventos ja existentes na agenda real (visualizacao e checagem de
duplicidade), sem OAuth. NAO cria, NAO altera e NAO envia convites: um feed ICS
e somente leitura.

Seguranca: a URL privada do ICS e um SEGREDO (equivale a uma senha de leitura
da agenda). Ela vem de variavel de ambiente (GOOGLE_CALENDAR_ICS_URL), nunca e
versionada e nunca deve ser registrada em log/auditoria.
"""

from __future__ import annotations

import ssl
import urllib.request
from dataclasses import dataclass


@dataclass
class IcsEvent:
    uid: str
    summary: str
    dtstart_raw: str
    dtend_raw: str = ""
    location: str = ""
    description: str = ""
    all_day: bool = False

    @property
    def date(self) -> str:
        """Data no formato YYYY-MM-DD, derivada de DTSTART."""
        v = self.dtstart_raw
        if len(v) >= 8 and v[:8].isdigit():
            return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"
        return ""

    @property
    def time(self) -> str:
        """Horario HH:MM, derivado de DTSTART; vazio se evento de dia inteiro."""
        if self.all_day:
            return ""
        v = self.dtstart_raw
        if "T" in v:
            hora = v.split("T", 1)[1]
            if len(hora) >= 4 and hora[:4].isdigit():
                return f"{hora[0:2]}:{hora[2:4]}"
        return ""


def unfold(text: str) -> list[str]:
    """Desfaz o "line folding" do RFC 5545 (continuacao por espaco/tab)."""
    linhas: list[str] = []
    for bruta in text.split("\n"):
        linha = bruta.rstrip("\r")
        if linha[:1] in (" ", "\t") and linhas:
            linhas[-1] += linha[1:]
        else:
            linhas.append(linha)
    return linhas


def _split_prop(linha: str) -> tuple[str, dict[str, str], str]:
    """Separa 'NOME;PARAM=...:VALOR' em (nome, params, valor)."""
    if ":" not in linha:
        return "", {}, ""
    cabecalho, valor = linha.split(":", 1)
    partes = cabecalho.split(";")
    nome = partes[0].upper()
    params: dict[str, str] = {}
    for p in partes[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k.upper()] = v
    return nome, params, valor


def parse_ics(text: str) -> list[IcsEvent]:
    """Converte o conteudo ICS em uma lista de IcsEvent."""
    eventos: list[IcsEvent] = []
    atual: dict[str, str] | None = None
    all_day = False

    for linha in unfold(text):
        if linha == "BEGIN:VEVENT":
            atual = {}
            all_day = False
            continue
        if linha == "END:VEVENT":
            if atual is not None:
                eventos.append(
                    IcsEvent(
                        uid=atual.get("UID", ""),
                        summary=atual.get("SUMMARY", ""),
                        dtstart_raw=atual.get("DTSTART", ""),
                        dtend_raw=atual.get("DTEND", ""),
                        location=atual.get("LOCATION", ""),
                        description=atual.get("DESCRIPTION", ""),
                        all_day=all_day,
                    )
                )
            atual = None
            continue
        if atual is None:
            continue

        nome, params, valor = _split_prop(linha)
        if nome in ("UID", "SUMMARY", "DTSTART", "DTEND", "LOCATION", "DESCRIPTION"):
            atual[nome] = valor
            if nome == "DTSTART" and params.get("VALUE", "").upper() == "DATE":
                all_day = True
    return eventos


def normalize_text(s: str) -> str:
    """Minusculo, sem espacos extras, para comparacao tolerante."""
    return " ".join((s or "").strip().lower().split())


def find_equivalent(
    eventos: list[IcsEvent],
    *,
    title: str,
    date: str,
    time: str = "",
    location: str = "",
    processo_sei: str = "",
) -> IcsEvent | None:
    """Procura, no calendario real, um evento equivalente ao novo (regra 7).

    Equivalencia exige a MESMA data e (titulo normalizado igual OU numero do
    processo SEI presente no texto do evento). Quando ambos tiverem horario,
    os horarios devem coincidir; idem para local. Datas diferentes nunca casam.
    """
    if not date:
        return None

    titulo_norm = normalize_text(title)
    local_norm = normalize_text(location)
    processo_norm = normalize_text(processo_sei)

    for ev in eventos:
        if ev.date != date:
            continue

        title_match = bool(titulo_norm) and normalize_text(ev.summary) == titulo_norm
        processo_match = False
        if processo_norm:
            blob = normalize_text(
                f"{ev.summary} {ev.location} {ev.description}"
            )
            processo_match = processo_norm in blob
        if not (title_match or processo_match):
            continue

        # Discriminadores adicionais quando ambos os lados tiverem o dado.
        if time and ev.time and time != ev.time:
            continue
        if local_norm and ev.location and normalize_text(ev.location) != local_norm:
            continue

        return ev
    return None


def fetch_ics(url: str, timeout: int = 30) -> str:
    """Baixa o conteudo do feed ICS. Levanta em caso de falha de rede."""
    if not url:
        raise ValueError("URL do feed ICS nao configurada (GOOGLE_CALENDAR_ICS_URL).")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8", "replace")


def read_calendar(url: str, timeout: int = 30) -> list[IcsEvent]:
    """Baixa e parseia o feed, devolvendo a lista de eventos."""
    return parse_ics(fetch_ics(url, timeout=timeout))


def calendar_collision_keys(eventos: list[IcsEvent]) -> set[str]:
    """Chaves normalizadas para detectar colisao com a agenda real.

    Formato: 'summary|data|horario|local' (tudo minusculo). Permite ao
    agenda_service evitar criar um evento que ja existe no calendario.
    """
    chaves: set[str] = set()
    for ev in eventos:
        partes = [ev.summary, ev.date, ev.time, ev.location]
        chaves.add("|".join(p.strip().lower() for p in partes))
    return chaves
