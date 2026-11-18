"""Environment-backed settings with secret-safe validation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from uuid import UUID

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    gemini_api_key: SecretStr = Field(validation_alias="GEMINI_API_KEY")
    gemini_model_planner: str = Field(validation_alias="GEMINI_MODEL_PLANNER")
    gemini_model_summarizer: str = Field(validation_alias="GEMINI_MODEL_SUMMARIZER")
    gemini_timeout_seconds: int = Field(
        default=30, ge=5, le=120, validation_alias="GEMINI_TIMEOUT_SECONDS"
    )
    gemini_retry_attempts: int = Field(
        default=2, ge=1, le=3, validation_alias="GEMINI_RETRY_ATTEMPTS"
    )

    fabric_auth_mode: str = Field(default="service_principal", validation_alias="FABRIC_AUTH_MODE")
    azure_tenant_id: UUID = Field(validation_alias="AZURE_TENANT_ID")
    azure_client_id: UUID = Field(validation_alias="AZURE_CLIENT_ID")
    azure_client_secret: SecretStr = Field(validation_alias="AZURE_CLIENT_SECRET")

    powerbi_workspace_id: UUID = Field(validation_alias="POWERBI_WORKSPACE_ID")
    powerbi_semantic_model_id: UUID = Field(validation_alias="POWERBI_SEMANTIC_MODEL_ID")
    powerbi_scope: str = Field(validation_alias="POWERBI_SCOPE")
    powerbi_api_base_url: str = Field(validation_alias="POWERBI_API_BASE_URL")

    powerbi_query_timeout_seconds: float = Field(
        default=30, ge=5, le=120, validation_alias="POWERBI_QUERY_TIMEOUT_SECONDS"
    )
    max_result_rows: int = Field(default=200, ge=1, le=500, validation_alias="MAX_RESULT_ROWS")
    max_summary_rows: int = Field(default=100, ge=1, le=200, validation_alias="MAX_SUMMARY_ROWS")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    semantic_catalog_path: Path = PROJECT_ROOT / "config" / "semantic_model.yaml"
    planner_prompt_path: Path = PROJECT_ROOT / "prompts" / "planner.md"
    summarizer_prompt_path: Path = PROJECT_ROOT / "prompts" / "summarizer.md"

    @field_validator("fabric_auth_mode")
    @classmethod
    def require_service_principal(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "service_principal":
            raise ValueError("MVP currently supports FABRIC_AUTH_MODE=service_principal only")
        return normalized

    @field_validator("powerbi_api_base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        value = value.rstrip("/")
        if not value.startswith("https://api.powerbi.com/"):
            raise ValueError("POWERBI_API_BASE_URL must use https://api.powerbi.com")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
