import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Booting up The Lenny Growth Assistant API...")
    await init_db()
    logger.info("Database initialized and ready.")
    
    # Auto-seed transcripts if database is empty (e.g. serverless cold start)
    try:
        from app.database import get_session_factory
        from app.models.db_models import TranscriptChunk
        from sqlalchemy import select, func
        session_factory = get_session_factory()
        if session_factory:
            async with session_factory() as session:
                count_res = await session.execute(select(func.count(TranscriptChunk.id)))
                count = count_res.scalar()
                if count == 0:
                    logger.info("No transcript chunks found in DB. Auto-seeding transcripts...")
                    from scripts.ingest import ingest_transcripts
                    await ingest_transcripts()
                    logger.info("Auto-seeding complete.")
    except Exception as e:
        logger.warning(f"Auto-seed check/execution skipped or failed: {e}")

    yield
    logger.info("Shutting down The Lenny Growth Assistant API...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack AI-powered conversational web application grounded in Lenny's Podcast transcripts.",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Register API Routers (both with /api prefix and root prefix for flexible reverse proxies)
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(sessions_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)

app.include_router(health_router, prefix="")
app.include_router(sessions_router, prefix="")
app.include_router(chat_router, prefix="")

@app.get("/")
@app.get("/api")
async def root():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }
