from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_USERNAME: str = os.getenv("REDIS_USERNAME", "root")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # 邮件配置
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.qq.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_TO: str = os.getenv("MAIL_TO", "")

    class Config:
        env_file = ".env"

settings = Settings() 