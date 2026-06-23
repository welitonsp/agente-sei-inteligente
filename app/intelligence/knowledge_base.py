"""Carregamento da knowledge base local do 19 CRPM.

Os arquivos sao CSV/Markdown locais, sem servico pago e sem IA externa.
Quando nao houver regra real, os consumidores devem retornar resultado
indefinido em vez de inventar unidade.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_KB_PATH = Path("knowledge_base") / "fluxos_19crpm"


@dataclass(frozen=True)
class Unit:
    codigo: str
    nome: str
    tipo: str = ""
    ativo: bool = True


@dataclass(frozen=True)
class KeywordRule:
    termo: str
    categoria: str = ""
    peso: float = 1.0
    interesse: str = "indefinido"
    ativo: bool = True


@dataclass(frozen=True)
class RoutingRule:
    id: str
    termos: tuple[str, ...]
    unidade_destino: str = ""
    tipo_minuta: str = ""
    providencia: str = ""
    interesse: str = "indefinido"
    prioridade: int = 0
    confianca: float = 0.0
    ativo: bool = True


@dataclass(frozen=True)
class LocalKnowledgeBase:
    unidades_19crpm: tuple[Unit, ...]
    unidades_alto_comando: tuple[Unit, ...]
    palavras_chave: tuple[KeywordRule, ...]
    regras_direcionamento: tuple[RoutingRule, ...]
    base_path: Path

    @property
    def has_real_rules(self) -> bool:
        return bool(self.palavras_chave or self.regras_direcionamento)

    def has_unit(self, name: str) -> bool:
        normalized = _normalize(name)
        return any(_normalize(unit.nome) == normalized for unit in self.unidades_19crpm)


def load_knowledge_base(base_path: str | Path = DEFAULT_KB_PATH) -> LocalKnowledgeBase:
    path = Path(base_path)
    return LocalKnowledgeBase(
        unidades_19crpm=tuple(_load_units(path / "unidades_19crpm.csv")),
        unidades_alto_comando=tuple(_load_units(path / "unidades_alto_comando.csv")),
        palavras_chave=tuple(_load_keywords(path / "palavras_chave_19crpm.csv")),
        regras_direcionamento=tuple(_load_routing_rules(path / "regras_direcionamento.csv")),
        base_path=path,
    )


def _load_units(path: Path) -> list[Unit]:
    rows = _read_csv(path)
    units = []
    for row in rows:
        if not _is_active(row):
            continue
        nome = str(row.get("nome", "")).strip()
        if not nome:
            continue
        units.append(
            Unit(
                codigo=str(row.get("codigo", "")).strip(),
                nome=nome,
                tipo=str(row.get("tipo", "")).strip(),
                ativo=True,
            )
        )
    return units


def _load_keywords(path: Path) -> list[KeywordRule]:
    rows = _read_csv(path)
    rules = []
    for row in rows:
        if not _is_active(row):
            continue
        termo = str(row.get("termo", "")).strip()
        if not termo:
            continue
        rules.append(
            KeywordRule(
                termo=termo,
                categoria=str(row.get("categoria", "")).strip(),
                peso=_float(row.get("peso"), default=1.0),
                interesse=str(row.get("interesse", "")).strip() or "indefinido",
                ativo=True,
            )
        )
    return rules


def _load_routing_rules(path: Path) -> list[RoutingRule]:
    rows = _read_csv(path)
    rules = []
    for row in rows:
        if not _is_active(row):
            continue
        termos = tuple(
            term.strip()
            for term in str(row.get("termos", "")).split(";")
            if term.strip()
        )
        if not termos:
            continue
        rules.append(
            RoutingRule(
                id=str(row.get("id", "")).strip(),
                termos=termos,
                unidade_destino=str(row.get("unidade_destino", "")).strip(),
                tipo_minuta=str(row.get("tipo_minuta", "")).strip(),
                providencia=str(row.get("providencia", "")).strip(),
                interesse=str(row.get("interesse", "")).strip() or "indefinido",
                prioridade=_int(row.get("prioridade"), default=0),
                confianca=_float(row.get("confianca"), default=0.0),
                ativo=True,
            )
        )
    return sorted(rules, key=lambda rule: rule.prioridade, reverse=True)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def _is_active(row: dict[str, str]) -> bool:
    value = str(row.get("ativo", "")).strip().lower()
    return value not in {"0", "false", "falso", "nao", "não", "n"}


def _int(value: object, *, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _float(value: object, *, default: float) -> float:
    try:
        return float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())
