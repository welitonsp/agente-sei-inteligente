from app.sei.browser_policy import check_automation_allowed, is_login_allowed, require_human_confirmation_for_draft

def test_automation_starts_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_SEI_BROWSER_AUTOMATION", "false")
    # Forçar recarregamento do config no teste
    from app.core.config import settings
    settings.ENABLE_SEI_BROWSER_AUTOMATION = False
    assert check_automation_allowed() is False

def test_is_login_allowed():
    from app.core.config import settings
    settings.SEI_BASE_URL = "https://sei.go.gov.br/sei/"
    assert is_login_allowed("https://sei.go.gov.br/sei/login") is True
    assert is_login_allowed("https://outrosite.com/login") is False

def test_draft_requires_human_confirmation():
    from app.core.config import settings
    settings.ENABLE_DRAFT_CREATION = False
    assert require_human_confirmation_for_draft() is True
