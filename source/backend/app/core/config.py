from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically resolve the path to the .env file.
# Search upwards from this file's location (up to 5 levels) to find it.
current_dir = Path(__file__).resolve().parent
env_file_path = None
for _ in range(6):
    candidate = current_dir / ".env"
    if candidate.exists() and candidate.is_file():
        env_file_path = candidate
        break
    current_dir = current_dir.parent

if env_file_path is None:
    env_file_path = Path.cwd() / ".env"
    if not env_file_path.exists():
        env_file_path = ".env"


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
