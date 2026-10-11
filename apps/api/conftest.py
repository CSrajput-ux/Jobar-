import pytest
import asyncio
from app.db.database import get_engine
from app.db.models import Base


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    engine = get_engine()

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # If loop is already running, create task
        loop.create_task(init_models())
    else:
        loop.run_until_complete(init_models())
