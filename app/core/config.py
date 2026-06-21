"""Configuracao central do agente, carregada de variaveis de ambiente (.env).

Os nomes seguem o .env.example. Flags de seguranca tem padrao SEGURO mesmo que
o .env esteja ausente. O agente recusa subir com ALLOW_OFFICIAL_SEI_ACTIONS
ligado, pois atos oficiais no SEI sao proibidos por design.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Aplicacao
    app_name: str = "Agente SEI Inteligente - 19 CRPM"
    app_env: str = "local"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    timezone: str = "America/Sao_Paulo"

    # Banco
    database_url: str = "sqlite:///./data/agente_sei.db"

    # Telegram / Agenda / e-mail ficam vazios ate a etapa correspondente.
    google_calendar_id: str = ""
    # URL privada do feed iCal (SEGREDO; somente leitura da agenda). Fica apenas
    # no .env local, nunca versionada.
    google_calendar_ics_url: str = ""
    # Backend de calendario: dry_run (simulacao) ou google (OAuth real, futuro).
    calendar_backend: str = "dry_run"

    # Origem dos convidados (Oficiais).
    #   google_contacts -> resolve e-mails a partir de um marcador/label do
    #                      Google Contatos via People API.
    #   group_email     -> usa um unico e-mail de grupo.
    officers_source: str = "google_contacts"
    officers_contact_label: str = "OFICIAIS"
    officers_group_email: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # SEI - travas de seguranca (padrao seguro)
    sei_base_url: str = "https://sei.go.gov.br/sei/"
    sei_mode: str = "assistido"
    sei_official_module_available: bool = False
    sei_allow_write_drafts: bool = False
    sei_store_passwords: bool = False
    sei_allow_shared_account: bool = False
    sei_data_mode: str = "local_only"
    sei_text_retention: str = "ephemeral"
    sei_allow_external_ai_for_live_content: bool = False
    sei_allow_browser_extension: bool = False

    # IA (provedor configuravel)
    ai_provider: str = ""
    ai_model: str = ""

    # Seguranca e auditoria
    log_level: str = "INFO"
    audit_log_retention_days: int = 365
    allow_official_sei_actions: bool = False

    @field_validator("allow_official_sei_actions")
    @classmethod
    def _atos_oficiais_proibidos(cls, value: bool) -> bool:
        if value:
            raise ValueError(
                "ALLOW_OFFICIAL_SEI_ACTIONS deve permanecer false. "
                "Atos oficiais no SEI sao proibidos por design (Regra de Ouro)."
            )
        return value

    @field_validator("sei_store_passwords", "sei_allow_shared_account")
    @classmethod
    def _travas_irreversiveis(cls, value: bool) -> bool:
        if value:
            raise ValueError(
                "Configuracao proibida: o agente nunca armazena senha do SEI "
                "nem usa conta compartilhada."
            )
        return value

    @field_validator("officers_source")
    @classmethod
    def _valida_origem_oficiais(cls, value: str) -> str:
        permitido = {"google_contacts", "group_email"}
        if value not in permitido:
            raise ValueError(
                f"OFFICERS_SOURCE invalido: '{value}'. Use um de {permitido}."
            )
        return value

    @property
    def officers_group_email_required(self) -> bool:
        """OFFICERS_GROUP_EMAIL so e obrigatorio no modo group_email."""
        return self.officers_source == "group_email"


@lru_cache
def get_settings() -> Settings:
    """Retorna a configuracao (cacheada) do processo."""
    return Settings()
