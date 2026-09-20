import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# State variable indicating whether we are using PostgreSQL or SQLite
IS_SQLITE_MODE = False
engine = None
AsyncSessionLocal = None

async def init_db():
    global engine, AsyncSessionLocal, IS_SQLITE_MODE
    
    # Try PostgreSQL first if configured
    if "postgresql" in settings.DATABASE_URL:
        try:
            test_engine = create_async_engine(
                settings.DATABASE_URL, 
                echo=settings.DEBUG,
                connect_args={"timeout": 5}
            )
            async with test_engine.connect() as conn:
                # Test connection
                pass
            engine = test_engine
            IS_SQLITE_MODE = False
            logger.info("Connected successfully to PostgreSQL database.")
        except Exception as e:
            logger.warning(
                f"PostgreSQL connection to {settings.DATABASE_URL} failed: {e}. "
                f"Switching gracefully to local SQLite fallback ({settings.SQLITE_FALLBACK_URL})."
            )
            engine = create_async_engine(settings.SQLITE_FALLBACK_URL, echo=settings.DEBUG)
            IS_SQLITE_MODE = True
    else:
        engine = create_async_engine(settings.SQLITE_FALLBACK_URL, echo=settings.DEBUG)
        IS_SQLITE_MODE = True

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info(f"Database initialized. Engine mode: {'SQLite (Local)' if IS_SQLITE_MODE else 'PostgreSQL (pgvector)'}")
    return AsyncSessionLocal

def get_session_factory():
    global AsyncSessionLocal
    return AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
