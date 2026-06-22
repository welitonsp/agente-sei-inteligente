from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./data/agente19.db"
    SEI_BASE_URL: str = "https://sei.go.gov.br/sei/"
    ENABLE_SEI_BROWSER_AUTOMATION: bool = False
    ENABLE_DRAFT_CREATION: bool = False
    ENABLE_GOOGLE_CALENDAR_DRY_RUN: bool = True
    LOG_FULL_TEXT: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
