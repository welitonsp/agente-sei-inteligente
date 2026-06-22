"""
browser_policy.py
Declarações das políticas rígidas de automação do Agente 19:
- login deve ocorrer apenas na página oficial do SEI.
- o agente não recebe senha.
- o agente não persiste cookie.
- automação real começa desabilitada por padrão.
- criação de minuta depende de confirmação humana e feature flag.
"""

from app.core.config import settings

def check_automation_allowed() -> bool:
    if not settings.ENABLE_SEI_BROWSER_AUTOMATION:
        return False
    return True

def is_login_allowed(url: str) -> bool:
    # Apenas a página oficial do SEI
    return url.startswith(settings.SEI_BASE_URL)

def require_human_confirmation_for_draft() -> bool:
    return not settings.ENABLE_DRAFT_CREATION
