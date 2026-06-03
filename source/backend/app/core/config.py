from pathlib import Path
from typing import Literal, Optional
from logging import getLogger

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger()


env_file = Path.cwd() / ".env"
if not env_file.is_file():
    env_file = Path.cwd() / ".env.test"
    if not env_file.is_file():
        raise RuntimeError(
            ".env file is required to run application. Move .env.example to .env"
        )
    logger.warning("Use test .env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    POSTGRES_DB: str

    ENVIRONMENT: Literal["development", "production"]
    TIMEZONE: str

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()