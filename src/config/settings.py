from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: str = Field(default="INFO")

    DATABASE_URL: str = Field(default="sqlite+pysqlite:///allocations.db")

    model_config = SettingsConfigDict()


settings = Settings()
