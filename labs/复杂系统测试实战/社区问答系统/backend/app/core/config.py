from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "社区问答系统"
    app_env: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite+pysqlite:///./community.db"
    redis_url: str = "redis://localhost:6379/0"
    ai_base_url: str = "http://localhost:8090"
    ai_summary_path: str = "/api/v1/forum/summarize"
    ai_timeout_seconds: float = Field(default=25.0, gt=0, le=120)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    auto_create_tables: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
