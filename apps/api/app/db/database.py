from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import settings


engine: AsyncEngine | None = None
SessionLocal = None


def get_engine() -> AsyncEngine:
    global engine, SessionLocal
    if engine is None:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is required")
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine


async def get_db() -> AsyncIterator:
    if SessionLocal is None:
        get_engine()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session
