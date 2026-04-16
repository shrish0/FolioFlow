# Core configuration using pydantic
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    telegram_bot_token: str
    webhook_url: str
    redis_url: str = "redis://localhost:6379/0"
    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"

settings = Settings()
