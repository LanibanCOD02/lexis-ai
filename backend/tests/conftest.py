import pytest
from fastapi.testclient import TestClient
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

# Add the parent directory to sys.path so app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy env vars for testing
os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"

from app.main import app
from app.db.session import get_db
from app.models.core import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def _run_setup():
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_init())

def _run_teardown():
    async def _drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.run(_drop())

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    _run_setup()
    yield
    _run_teardown()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
