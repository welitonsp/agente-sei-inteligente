"""Guarda de regressão contra mojibake (codificação dupla CP1252/UTF-8).

Garante que (1) o corretor funciona, (2) acentos legítimos são preservados e
(3) nenhum arquivo de texto versionado volta a conter mojibake. Este último
teste falha o CI se alguém recommitar texto corrompido.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fix_mojibake import fix_text, iter_text_files  # noqa: E402


def test_fix_text_corrige_mojibake_conhecido():
    assert fix_text("informaÃ§Ã£o") == "informação"
    assert fix_text("anÃ¡lise") == "análise"
    assert fix_text("OfÃ­cio") == "Ofício"
    assert fix_text("revisÃ£o") == "revisão"


def test_fix_text_preserva_acentos_legitimos():
    # "NÃO" tem um "Ã" legítimo seguido de "O" (ASCII) e não pode ser alterado.
    assert fix_text("NÃO habilita") == "NÃO habilita"
    # Acentos já corretos permanecem intactos.
    assert fix_text("Operação válida à noite") == "Operação válida à noite"


def test_fix_text_eh_idempotente():
    once = fix_text("criaÃ§Ã£o de minuta")
    assert fix_text(once) == once


def test_repositorio_sem_mojibake():
    """Nenhum arquivo de texto versionado deve conter mojibake."""
    pendentes = []
    for path in iter_text_files(ROOT):
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if fix_text(original) != original:
            pendentes.append(str(path.relative_to(ROOT)))
    assert not pendentes, f"Arquivos com mojibake: {pendentes}"
