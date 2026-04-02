from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # AI Configuration
    AI_BASE_URL: str
    AI_API_KEY: str
    AI_MODEL: str = "gpt-4"

    # App Settings
    APP_NAME: str = "InfoHub"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./data/infohub.db"

    # News Sources
    NEWSAPI_KEY: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
