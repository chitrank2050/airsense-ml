"""
Database connection and session management.

Provides async SQLAlchemy engine and session factory for FastAPI
dependency injection. Uses asyncpg driver for async PostgreSQL access.

Responsibility: manage database connections. Nothing else.
Does NOT: define models, run queries, or handle business logic.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings
from src.core.logger import logger


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# Async engine — used by FastAPI at runtime
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # set True for SQL query logging during development
    pool_size=5,  # connections kept alive in pool
    max_overflow=10,  # extra connections allowed above pool_size
    pool_pre_ping=True,  # verify connection before use — handles Supabase wakeup
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Create all tables defined in ORM models.
    Called once at application startup via lifespan.

    Does NOT run migrations — use Alembic for schema changes.
    """
    async with engine.begin() as conn:
        # Dispose any cached connections first
        await engine.dispose()
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised")
