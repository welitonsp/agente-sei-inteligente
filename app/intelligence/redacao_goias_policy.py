"""Policy deterministica do Manual de Redacao do Governo de Goias (FASE 65).

Avalia uma minuta gerada contra as regras de redacao oficial e devolve um
checklist testavel. E um **guardrail deterministico**, nao uma chamada de LLM:
alinha-se a filosofia do projeto de que a barreira e codigo auditavel, nao o
prompt. Base de regras curada em `knowledge_base/redacao_goias/regras_redacao.md`.

Separa dois niveis de problema:
- **bloqueante**: a minuta afirma ato que o agente nao pode praticar, simula
  assinatura ou expoe dado sensivel. Reprova (`ok=False`, `bloqueado=True`).
- **pendencia**: falta fecho, forma de tratamento, estrutura, ha placeholder a
  preencher ou quebra de impessoalidade. Nao bloqueia, mas exige ajuste humano.

Principio mantido: conhecimento nao vira permissao — esta policy nao pratica
ato; apenas avalia texto e sinaliza. Revisao humana continua obrigatoria.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

# Fechos oficiais aceitos (normalizados sem acento).
_FECHOS_VALIDOS = ("respeitosamente", "atenciosamente")

# Tipos que sao documentos enderecados: exigem fecho e forma de tratamento.
_TIPOS_ENDERECADOS = frozenset({"oficio", "memorando", "parte"})

# Cabecalho/estrutura minima esperada por tipo (termos normalizados).
_ESTRUTURA_ESPERADA: dict[str, tuple[str, ...]] = {
    "despacho": ("despacho", "processo"),
    "oficio": ("oficio", "assunto"),
    "informacao": ("informacao", "processo"),
    "encaminhamento": ("encaminhamento", "processo"),
    "memorando": ("memorando", "assunto"),
    "parte": ("parte", "assunto"),
    "portaria": ("portaria", "resolve"),
}

# Formas de tratamento reconhecidas (normalizadas).
_FORMAS_TRATAMENTO = (
    "vossa senhoria",
    "vossa excelencia",
    "senhor",
    "senhora",
    "v. sa",
    "v. exa",
)

# Primeira pessoa do singular -> quebra de impessoalidade.
_PRIMEIRA_PESSOA = re.compile(r"\b(eu|meu|minha|meus|minhas|comigo|mim)\b")

# Promessa, em primeira pessoa, de ato que o agente nao pode praticar.
_PROMESSA_ATO = re.compile(
    r"\b(assino|assinei|assinarei|tramito|tramitei|tramitarei|"
    r"envio o processo|enviei o processo|concluo|conclui o processo|"
    r"dou ciencia|arquivo o processo)\b"
)

# Assinatura simulada dentro da minuta.
_ASSINATURA_SIMULADA = re.compile(
    r"assinado\s+(eletronicamente|digitalmente)|"
    r"documento\s+assinado|assinatura\s+eletronica"
)

# Placeholders legitimos deixados para o humano.
_PLACEHOLDER = re.compile(r"\[preencher[^\]]*\]|\[[a-z_]+\]")

# Sinais de dado sensivel que nunca devem aparecer na minuta.
_DADO_SENSIVEL = re.compile(
    r"\bsenha\b|\bcpf\b|\bcookie\b|\btoken\b|\bsessao\b|password"
)


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    descricao: str
    ok: bool
    bloqueante: bool = False
    detalhe: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "descricao": self.descricao,
            "ok": self.ok,
            "bloqueante": self.bloqueante,
            "detalhe": self.detalhe,
        }


@dataclass(frozen=True)
class RedacaoVerdict:
    ok: bool
    bloqueado: bool
    score: float
    pendencias: list[str]
    bloqueios: list[str]
    checklist: list[ChecklistItem] = field(default_factory=list)

    def to_contract(self) -> dict[str, Any]:
        # Formato compativel com o campo `redacao_goias` de docs/65.
        return {
            "ok": self.ok,
            "bloqueado": self.bloqueado,
            "score": self.score,
            "pendencias": self.pendencias,
            "bloqueios": self.bloqueios,
            "checklist": [item.to_contract() for item in self.checklist],
            "revisao_humana_obrigatoria": True,
        }


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _longest_sentence_words(text: str) -> int:
    frases = re.split(r"[.!?;\n]+", text)
    return max((len(f.split()) for f in frases if f.strip()), default=0)


def evaluate_redacao(
    texto: str, tipo_minuta: str = "", texto_base: str = ""
) -> RedacaoVerdict:
    """Avalia a minuta contra o checklist do Manual de Redacao de Goias."""
    norm = _normalize(texto)
    tipo = _normalize(tipo_minuta)
    itens: list[ChecklistItem] = []

    def add(id_: str, desc: str, ok: bool, *, bloqueante: bool = False, detalhe: str = "") -> None:
        itens.append(ChecklistItem(id_, desc, ok, bloqueante, detalhe))

    # 1. Finalidade/assunto presente.
    tem_assunto = "assunto" in norm or "processo" in norm or len(norm) > 60
    add("finalidade_clara", "Finalidade/assunto do documento esta clara", tem_assunto,
        detalhe="" if tem_assunto else "Nao identifiquei assunto/processo.")

    # 2. Impessoalidade.
    impessoal = not _PRIMEIRA_PESSOA.search(norm)
    add("impessoalidade", "Texto impessoal (sem 1a pessoa do singular)", impessoal,
        detalhe="" if impessoal else "Ha marcas de primeira pessoa do singular.")

    # 3. Clareza/concisao (heuristica de frase muito longa).
    frase_longa = _longest_sentence_words(norm)
    conciso = frase_longa <= 60
    add("clareza_concisao", "Frases claras e concisas", conciso,
        detalhe="" if conciso else f"Frase com {frase_longa} palavras; considere dividir.")

    # 4/6. Estrutura completa por tipo documental.
    esperados = _ESTRUTURA_ESPERADA.get(tipo, ())
    faltando = [t for t in esperados if t not in norm]
    estrutura_ok = not faltando if esperados else True
    add("estrutura_completa", "Estrutura completa para o tipo documental", estrutura_ok,
        detalhe="" if estrutura_ok else f"Faltam elementos: {', '.join(faltando)}.")

    # 5. Forma de tratamento (para documentos enderecados).
    if tipo in _TIPOS_ENDERECADOS:
        tem_tratamento = any(f in norm for f in _FORMAS_TRATAMENTO) or bool(_PLACEHOLDER.search(norm))
        add("forma_tratamento", "Forma de tratamento adequada", tem_tratamento,
            detalhe="" if tem_tratamento else "Documento enderecado sem forma de tratamento.")

    # 7. Fecho adequado (para documentos enderecados).
    if tipo in _TIPOS_ENDERECADOS:
        tem_fecho = any(f in norm for f in _FECHOS_VALIDOS)
        add("fecho_adequado", "Fecho adequado (Respeitosamente/Atenciosamente)", tem_fecho,
            detalhe="" if tem_fecho else "Falta fecho oficial.")

    # 8. Nao prometer ato proibido (BLOQUEANTE).
    promessa = _PROMESSA_ATO.search(norm)
    add("sem_promessa_ato", "Nao promete ato que o agente nao pratica", not promessa,
        bloqueante=True,
        detalhe="" if not promessa else f"Promessa de ato proibido: '{promessa.group(0)}'.")

    # 9. Nao simular assinatura (BLOQUEANTE).
    assinatura = _ASSINATURA_SIMULADA.search(norm)
    add("sem_assinatura_simulada", "Nao simula assinatura", not assinatura,
        bloqueante=True,
        detalhe="" if not assinatura else "Ha simulacao de assinatura no texto.")

    # 10. Sem dado sensivel (BLOQUEANTE).
    sensivel = _DADO_SENSIVEL.search(norm)
    add("sem_dado_sensivel", "Nao expoe senha/token/CPF/cookie", not sensivel,
        bloqueante=True,
        detalhe="" if not sensivel else "Possivel dado sensivel exposto.")

    # 11. Campos pendentes marcados (informativo; placeholder e comportamento correto).
    placeholders = _PLACEHOLDER.findall(norm)
    add("campos_pendentes_marcados", "Campos ausentes marcados com placeholder",
        not placeholders,
        detalhe="" if not placeholders else f"{len(placeholders)} campo(s) a preencher.")

    # Consolidacao.
    bloqueios = [f"{i.descricao}: {i.detalhe}" for i in itens if i.bloqueante and not i.ok]
    pendencias = [
        f"{i.descricao}: {i.detalhe}".strip(": ").strip()
        for i in itens
        if not i.bloqueante and not i.ok
    ]
    bloqueado = bool(bloqueios)
    ok = not bloqueado and not pendencias
    score = round(sum(1 for i in itens if i.ok) / len(itens), 2) if itens else 0.0

    return RedacaoVerdict(
        ok=ok,
        bloqueado=bloqueado,
        score=score,
        pendencias=pendencias,
        bloqueios=bloqueios,
        checklist=itens,
    )


__all__ = ["ChecklistItem", "RedacaoVerdict", "evaluate_redacao"]
