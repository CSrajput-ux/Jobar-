from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import settings


engine: AsyncEngine | None = None
SessionLocal = None


def get_engine() -> AsyncEngine:
    global engine, SessionLocal
    if engine is None:
        database_url = settings.get_database_url()
        if "sqlite" in database_url:
            engine = create_async_engine(database_url, pool_pre_ping=True)
        else:
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
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
