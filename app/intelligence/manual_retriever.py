"""Retriever RAG local dos manuais (custo zero, deterministico, sem rede).

Da ao Agente 19 a inteligencia dos manuais (SEI e Redacao de Goias) para
classificar, redigir e reconhecer limites com fundamentacao — sem inventar
procedimento. Ver `docs/17`, `docs/65` e o principio "conhecimento != permissao".

Design (nivel de engenharia de agentes):
- **Zero custo/dependencia**: nenhuma embedding paga nem pacote novo. Ranqueia
  por sobreposicao de termos ponderada por IDF sobre a base curada local.
- **Deterministico e offline**: mesmo input, mesmo output; roda em testes e no
  caminho custo-zero.
- **Grounding com fonte**: cada trecho retornado carrega o arquivo/titulo de
  origem, para a saida ser defensavel.
- **So conhecimento**: o retriever nunca executa acao no SEI; e leitura pura.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Diretorios da base curada. Cada .md e fatiado por titulos `##` em regras.
DEFAULT_SOURCE_DIRS: tuple[Path, ...] = (
    _REPO_ROOT / "knowledge_base" / "manual_sei",
    _REPO_ROOT / "knowledge_base" / "redacao_goias",
)

# Palavras muito comuns que nao ajudam a distinguir regras (pt-br).
_STOPWORDS = frozenset(
    """
    a o e de do da das dos em no na nos nas um uma que se por para com sem sob
    ao aos as os e ou nao sim ser sao ter tem the of and to in is
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _strip_accents(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    """Normaliza (sem acento, minusculo), remove stopwords e tokens curtos."""
    norm = _strip_accents(text).lower()
    return [
        tok
        for tok in _TOKEN_RE.findall(norm)
        if len(tok) > 2 and tok not in _STOPWORDS
    ]


@dataclass(frozen=True)
class Chunk:
    source: str  # nome do arquivo de origem
    title: str  # titulo da regra (heading)
    text: str  # corpo completo da regra
    tokens: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float


def _split_markdown(content: str, source: str) -> list[Chunk]:
    """Fatia o markdown em regras: cada bloco iniciado por `## ` vira um Chunk."""
    chunks: list[Chunk] = []
    title = ""
    body: list[str] = []

    def flush() -> None:
        if title:
            text = f"{title}\n" + "\n".join(body).strip()
            tokens = frozenset(tokenize(title + " " + " ".join(body)))
            if tokens:
                chunks.append(Chunk(source=source, title=title, text=text.strip(), tokens=tokens))

    for line in content.splitlines():
        if line.startswith("## "):
            flush()
            title = line[3:].strip()
            body = []
        elif line.startswith("# "):
            # Titulo H1 do arquivo: nao inicia regra, apenas ignora.
            continue
        else:
            body.append(line)
    flush()
    return chunks


def load_chunks(source_dirs: tuple[Path, ...] = DEFAULT_SOURCE_DIRS) -> list[Chunk]:
    chunks: list[Chunk] = []
    for directory in source_dirs:
        if not directory.exists():
            continue
        for md in sorted(directory.glob("*.md")):
            if md.name.upper() in {"README.MD", "COMO_PREENCHER.MD"}:
                continue
            try:
                content = md.read_text(encoding="utf-8")
            except OSError:
                continue
            chunks.extend(_split_markdown(content, md.name))
    return chunks


class ManualRetriever:
    """Ranqueia regras curadas por sobreposicao de termos ponderada por IDF."""

    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks
        n = len(chunks)
        df: dict[str, int] = {}
        for chunk in chunks:
            for token in chunk.tokens:
                df[token] = df.get(token, 0) + 1
        # IDF suavizado: termos raros pesam mais; termos onipresentes, quase nada.
        self._idf = {
            token: math.log((n + 1) / (freq + 1)) + 1.0 for token, freq in df.items()
        }

    @property
    def size(self) -> int:
        return len(self._chunks)

    def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        query_tokens = set(tokenize(query))
        if not query_tokens or not self._chunks:
            return []
        scored: list[RetrievedChunk] = []
        for chunk in self._chunks:
            overlap = query_tokens & chunk.tokens
            if not overlap:
                continue
            score = sum(self._idf.get(tok, 1.0) for tok in overlap)
            scored.append(RetrievedChunk(chunk=chunk, score=round(score, 4)))
        # Ordena por score desc; desempate estavel por fonte+titulo.
        scored.sort(key=lambda rc: (-rc.score, rc.chunk.source, rc.chunk.title))
        return scored[:k]


@lru_cache(maxsize=1)
def get_default_retriever() -> ManualRetriever:
    """Retriever cacheado sobre a base curada padrao."""
    return ManualRetriever(load_chunks())


def retrieve_context(query: str, k: int = 4) -> str:
    """Contexto formatado e com fonte para injetar no RAG. Resiliente a falhas."""
    try:
        results = get_default_retriever().retrieve(query, k=k)
    except Exception:
        return ""
    if not results:
        return ""
    linhas = ["REGRAS DOS MANUAIS (fonte oficial curada — consulta, nao permissao):"]
    for rc in results:
        linhas.append(f"\n[{rc.chunk.source} :: {rc.chunk.title}]\n{rc.chunk.text}")
    return "\n".join(linhas)


__all__ = [
    "Chunk",
    "ManualRetriever",
    "RetrievedChunk",
    "get_default_retriever",
    "load_chunks",
    "retrieve_context",
    "tokenize",
]
