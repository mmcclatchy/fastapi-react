import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine, AsyncSession

from db.database import get_session
from main import app
from utils.settings import settings


test_async_engine = AsyncEngine(create_engine(settings.test_db_url, echo=True, future=True))


pytest_plugins = ["tests.fixtures.accounts"]


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncSession:
    test_async_session = sessionmaker(
        test_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_async_session() as s:
        app.dependency_overrides[get_session] = lambda: s
        async with test_async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        yield s

    async with test_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await test_async_engine.dispose()


@pytest_asyncio.fixture
async def client(event_loop, session):
    async with AsyncClient(app=app, base_url=f"{settings.api_base_url}/v1") as c:
        yield c
