from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolves to AutoResolve/ regardless of where uvicorn is invoked from
_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/autoresolve"
    )
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    # LLM routing
    llm_primary: str = "ollama"
    llm_fallback: str = "gemini"
    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    # GitHub
    github_token: str = ""
    webhook_secret: str = ""
    # AWS
    s3_bucket: str = "autoresolve-logs"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    # App
    cors_origins: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=str(_ROOT / "infra" / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()