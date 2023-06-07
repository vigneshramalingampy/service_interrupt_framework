from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv(".env")


class AppSettings(BaseSettings):
    database_url: str = "postgresql+asyncpg://database:database@database:5432/service_interrupt"
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return AppSettings()


settings = get_settings()
