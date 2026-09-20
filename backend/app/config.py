import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Load .env from current directory or parent directory
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

class Settings(BaseSettings):
    APP_NAME: str = "The Lenny Growth Assistant"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    
    # Persistence
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant"
    )
    _db_path: str = "/tmp/lenny_assistant.db" if (os.getenv("VERCEL") or (os.name != "nt" and os.path.exists("/tmp"))) else "./lenny_assistant.db"
    SQLITE_FALLBACK_URL: str = os.getenv("SQLITE_FALLBACK_URL", f"sqlite+aiosqlite:///{_db_path}")

    # LLM Providers
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    
    # Cloud Providers (Optional)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # RAG Settings
    EMBEDDING_DIM: int = 384
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.20

    class Config:
        env_file = [".env", "../.env"]
        extra = "allow"

settings = Settings()
