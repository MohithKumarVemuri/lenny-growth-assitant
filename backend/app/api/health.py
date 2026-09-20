import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import app.database as db_mod
from app.models.db_models import TranscriptChunk
from app.models.schemas import HealthResponse
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health Probe"])

@router.get("", response_model=HealthResponse)
async def check_health(db: AsyncSession = Depends(db_mod.get_db)):
    # 1. Check vector / chunk count
    vector_count = 0
    try:
        stmt = select(func.count(TranscriptChunk.id))
        res = await db.execute(stmt)
        vector_count = res.scalar() or 0
    except Exception as e:
        logger.warning(f"Error querying transcript chunk count: {e}")

    # 2. Check Ollama
    ollama = OllamaProvider()
    ollama_reachable = await ollama.is_available()
    ollama_models = await ollama.get_models() if ollama_reachable else []

    # 3. Check Cloud Providers
    claude = ClaudeProvider()
    claude_ready = await claude.is_available()
    openai = OpenAIProvider()
    openai_ready = await openai.is_available()

    is_sqlite = db_mod.IS_SQLITE_MODE or (db.bind and "sqlite" in str(db.bind.url))

    return HealthResponse(
        status="healthy",
        database_mode="sqlite_local" if is_sqlite else "postgresql_pgvector",
        vector_count=vector_count,
        default_provider=settings.DEFAULT_PROVIDER,
        ollama_status={
            "online": ollama_reachable,
            "base_url": settings.OLLAMA_BASE_URL,
            "target_model": settings.OLLAMA_MODEL,
            "installed_models": ollama_models
        },
        cloud_configured={
            "anthropic": claude_ready,
            "openai": openai_ready
        }
    )
