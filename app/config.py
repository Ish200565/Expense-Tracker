from datetime import timedelta

from dotenv import load_dotenv
import os

load_dotenv()


def configured_origins():
    value = os.getenv("CORS_ORIGINS", "https://ish200565.github.io")
    return [origin.strip() for origin in value.split(",") if origin.strip()]

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith(("postgresql://", "postgres://")):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 240,
            "pool_timeout": 30,
        }
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    CORS_ORIGINS = configured_origins()
