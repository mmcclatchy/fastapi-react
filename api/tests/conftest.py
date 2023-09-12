import asyncio
import os
from typing import Generator

import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine, AsyncSession

from db.database import engine
from main import app
from settings import API_V1_PREFIX, TEST_DB_URL


test_async_engine = AsyncEngine(create_engine(TEST_DB_URL, echo=True, future=True))


async def database_exists(db_url: str) -> bool:
    conn = await asyncpg.connect(db_url)
    try:
        await conn.fetchval("SELECT 1")
        return True
    except asyncpg.exceptions.UndefinedTableError:
        return False
    finally:
        await conn.close()


def get_fixture_filenames():
    """
    Formats files within fixtures subdirectory to be added as pytest plugins

    Note: This is overkill for a small app
    """
    filenames = []
    cur_dir = os.getcwd()
    fixture_dir = f"{cur_dir}/fixtures"
    for root, _, files in os.walk(fixture_dir):
        abs_path = root.split("/")
        if any(d.startswith((".", "_")) for d in abs_path):
            continue
        tests_idx = abs_path.index("tests")
        subdirectory_path = ".".join(abs_path[tests_idx:])
        for file in files:
            filename, extension = os.path.splitext(file)
            if not extension == ".py" or filename.startswith("_"):
                continue
            filenames.append(f"{subdirectory_path}.{filename}")
    return filenames


# pytest_plugins = get_fixture_filenames()
pytest_plugins = ["tests.fixtures.accounts"]


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(event_loop, session):
    async with AsyncClient(app=app, base_url=API_V1_PREFIX) as c:
        yield c
