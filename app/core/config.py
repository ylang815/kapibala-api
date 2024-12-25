from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_USERNAME: str = os.getenv("REDIS_USERNAME", "root")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    class Config:
        env_file = ".env"

settings = Settings() 