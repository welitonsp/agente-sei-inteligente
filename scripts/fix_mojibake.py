"""Corretor determinístico de mojibake (codificação dupla CP1252/UTF-8).

Contexto: vários arquivos de texto do repositório foram salvos com UTF-8
codificado em dobro (ex.: "informação" virou "informaÃ§Ã£o"). Este utilitário
substitui APENAS sequências de mojibake conhecidas por seus caracteres
corretos. Ele nunca toca em acentos já válidos isolados (ex.: o "Ã" legítimo
de "NÃO" é preservado, pois só convertemos combinações multi-caractere).

Uso:
    python scripts/fix_mojibake.py --check .      # apenas relata (não grava)
    python scripts/fix_mojibake.py --apply .      # corrige no lugar

Seguro por desenho:
- Determinístico: tabela fixa de substituições.
- Idempotente: rodar duas vezes não muda nada na segunda.
- Não-destrutivo em --check.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Mapa de mojibake -> caractere correto.
# As chaves são combinações multi-caractere que NÃO ocorrem em português
# correto, garantindo que acentos válidos isolados jamais sejam alterados.
MOJIBAKE_MAP: dict[str, str] = {
    # Minúsculas acentuadas
    "Ã¡": "á", "Ã ": "à", "Ã¢": "â", "Ã£": "ã", "Ã¤": "ä",
    "Ã©": "é", "Ã¨": "è", "Ãª": "ê", "Ã«": "ë",
    "Ã­": "í", "Ã¬": "ì", "Ã®": "î", "Ã¯": "ï",
    "Ã³": "ó", "Ã²": "ò", "Ã´": "ô", "Ãµ": "õ", "Ã¶": "ö",
    "Ãº": "ú", "Ã¹": "ù", "Ã»": "û", "Ã¼": "ü",
    "Ã§": "ç", "Ã±": "ñ", "Ã½": "ý",
    # Maiúsculas acentuadas comuns em português
    "Ã€": "À", "Ã‚": "Â", "Ãƒ": "Ã", "Ã„": "Ä",
    "Ã‰": "É", "Ãˆ": "È", "ÃŠ": "Ê",
    "Ã“": "Ó", "Ã’": "Ò", "Ã”": "Ô", "Ã•": "Õ",
    "Ãš": "Ú", "Ã™": "Ù",
    "Ã‡": "Ç", "Ã‘": "Ñ",
    # Símbolos com prefixo "Â" espúrio
    "Âº": "º", "Â°": "°", "Âª": "ª", "Â§": "§", "Â´": "´", "Â·": "·",
    "Â": "", "â‚¬": "€",
}

# Extensões de texto que processamos.
TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".csv", ".yml", ".yaml",
                 ".html", ".css", ".js", ".cfg", ".ini", ".toml"}

# Diretórios ignorados.
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache",
             ".pytest_cache", ".ruff_cache"}

# Arquivos que contêm sequências de mojibake de forma intencional (o próprio
# corretor e seu teste-guarda) e portanto não devem ser reescritos.
SKIP_FILES = {"fix_mojibake.py", "test_mojibake_guard.py"}


def fix_text(text: str) -> str:
    """Aplica todas as substituições de mojibake ao texto."""
    for bad, good in MOJIBAKE_MAP.items():
        if bad in text:
            text = text.replace(bad, good)
    return text


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Corrige mojibake (codificação dupla).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Apenas relata, não grava.")
    group.add_argument("--apply", action="store_true", help="Corrige os arquivos no lugar.")
    parser.add_argument("root", nargs="?", default=".", help="Raiz a varrer (padrão: .).")
    args = parser.parse_args(argv)

    root = Path(args.root)
    affected = 0
    total_replacements = 0

    for path in iter_text_files(root):
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        fixed = fix_text(original)
        if fixed == original:
            continue

        affected += 1
        # Conta substituições para o relatório.
        n = sum(original.count(bad) for bad in MOJIBAKE_MAP if bad in original)
        total_replacements += n
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"[{'CORRIGIDO' if args.apply else 'PENDENTE '}] {rel} ({n} ocorrências)")

        if args.apply:
            path.write_text(fixed, encoding="utf-8", newline="\n")

    print("-" * 60)
    verbo = "corrigidos" if args.apply else "com mojibake"
    print(f"{affected} arquivo(s) {verbo}; {total_replacements} substituição(ões).")
    if args.check and affected:
        # Código de saída != 0 permite uso como gate em CI.
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
