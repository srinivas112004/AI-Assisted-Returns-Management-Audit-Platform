import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"

default_db_path = (BACKEND_DIR / "app.db").resolve().as_posix()

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Yotaa AI Returns Management & Audit Platform"
    API_V1_STR: str = "/api"
    
    # Database - Default to absolute SQLite path for seamless execution from any CWD
    DATABASE_URL: str = f"sqlite:///{default_db_path}"
    
    # Synthetic Data Generation
    RANDOM_SEED: int = 20261022
    
    # Security
    ADMIN_API_KEY: str = "yotaa-secure-admin-token-2026"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Normalize sqlite path if relative in env
if settings.DATABASE_URL.startswith("sqlite:///./"):
    rel = settings.DATABASE_URL.replace("sqlite:///./", "")
    settings.DATABASE_URL = f"sqlite:///{(BASE_DIR / rel).resolve().as_posix()}"
