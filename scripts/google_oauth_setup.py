"""Gera o refresh token OAuth do Google (executar UMA vez, localmente).

Pre-requisitos:
1. Criar um projeto no Google Cloud Console.
2. Ativar as APIs: Google Calendar API e People API.
3. Criar credencial OAuth do tipo "Desktop app".
4. Colocar no .env local:
       GOOGLE_CLIENT_ID=...
       GOOGLE_CLIENT_SECRET=...

Uso (no terminal do projeto):
    ! .venv/Scripts/python.exe scripts/google_oauth_setup.py

O script abre o navegador para consentimento e imprime o refresh token.
Copie o valor para o .env:
    GOOGLE_REFRESH_TOKEN=<valor_impresso>

O refresh token e um SEGREDO: nunca versione, nunca compartilhe, nunca logue.
"""

from __future__ import annotations

import sys

from app.core.config import get_settings
from app.integrations.google_auth import SCOPES, TOKEN_URI


def main() -> int:
    settings = get_settings()
    if not (settings.google_client_id and settings.google_client_secret):
        print(
            "ERRO: defina GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env antes "
            "de rodar este script."
        )
        return 1

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
    except ImportError:
        print("ERRO: instale as dependencias Google (requirements.txt).")
        return 1

    client_config = {
        "installed": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": TOKEN_URI,
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    # access_type=offline + prompt=consent garante o refresh token.
    creds = flow.run_local_server(
        port=0, access_type="offline", prompt="consent"
    )

    if not creds.refresh_token:
        print(
            "ATENCAO: nenhum refresh token retornado. Remova o acesso anterior "
            "em https://myaccount.google.com/permissions e rode novamente."
        )
        return 1

    print("\n=== SUCESSO ===")
    print("Copie a linha abaixo para o seu .env local:\n")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("\nEscopos autorizados:")
    for s in SCOPES:
        print(f"  - {s}")
    print("\nNAO versione nem compartilhe esse valor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
