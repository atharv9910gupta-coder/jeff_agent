# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # Email (SMTP)
    SMTP_HOST: str = None
    SMTP_PORT: int = 587
    SMTP_USER: str = None
    SMTP_PASS: str = None
    EMAIL_FROM: str = None

    # Twilio (optional)
    TWILIO_SID: str = None
    TWILIO_TOKEN: str = None
    TWILIO_FROM: str = None

    # Frontend origins
    FRONTEND_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
