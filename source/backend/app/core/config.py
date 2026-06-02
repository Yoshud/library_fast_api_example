from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> Path:
    # 1. Check current working directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        return cwd_env

    # 2. Check relative to this file's position
    this_file = Path(__file__).resolve()

    # Project root (momentum_interview/.env) - 5 directories up from core/config.py
    if len(this_file.parents) >= 5:
        root_env = this_file.parents[4] / ".env"
        if root_env.is_file():
            return root_env

    # 3. Backend root (source/backend/.env or /source/.env) - 3 directories up from core/config.py
    if len(this_file.parents) >= 3:
        backend_env = this_file.parents[2] / ".env"
        if backend_env.is_file():
            return backend_env

    raise RuntimeError(
        ".env file is required to run application. Move .env.example to .env"
    )


env_file_path = _resolve_env_file()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    POSTGRES_USER: str = "test"
    POSTGRES_PASSWORD: str = "test"
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    POSTGRES_DB: str = "test"

    ENVIRONMENT: str = "development"
    TIMEZONE: str = "UTC"

    if ENVIRONMENT not in ["development", "production"]:
        raise RuntimeError("ENVIRONMENT should be equal 'development' or 'production'")

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
