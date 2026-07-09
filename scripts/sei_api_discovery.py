"""Diagnostico seguro de endpoints SEI/WSSEI.

Uso:
    python scripts/sei_api_discovery.py

Nao envia usuario, senha, cookie, token ou sessao. Nao tenta executar operacao
de negocio. Apenas consulta URLs candidatas sem credenciais.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.sei.api_discovery import discover_public_api  # noqa: E402


def main() -> int:
    settings = get_settings()
    print("Diagnostico seguro de API SEI/WSSEI")
    print(f"Base SEI: {settings.sei_base_url}")
    print("Credenciais: nao enviadas")
    print()

    for result in discover_public_api(settings):
        status = result.http_status if result.http_status is not None else "-"
        print(f"[{result.classification}] {result.name}")
        print(f"  URL: {result.url}")
        print(f"  HTTP: {status}")
        print(f"  Detalhe: {result.detail}")
        print()

    print("Observacao: resultado positivo nao autoriza uso real da API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
