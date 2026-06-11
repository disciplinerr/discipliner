from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://discipliner:discipliner@localhost:5432/discipliner"
    ANTHROPIC_API_KEY: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:3000"

    CLAUDE_MODEL: str = "claude-fable-5"
    CHALLENGE_MAX_TOKENS: int = 800
    EVALUATION_MAX_TOKENS: int = 100

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v or v in ("change-me", "secret", "dev"):
            raise ValueError(
                "SECRET_KEY must be set to a strong random value (e.g. openssl rand -hex 32)"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
