from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://discipliner:discipliner@localhost:5432/discipliner"
    ANTHROPIC_API_KEY: str = ""
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CLAUDE_MODEL: str = "claude-fable-5"
    CHALLENGE_MAX_TOKENS: int = 800
    EVALUATION_MAX_TOKENS: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
