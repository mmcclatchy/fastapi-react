from os import environ

from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine, AsyncSession

from settings import DB_URL, TEST_DB_URL


# default_db_url = (
#     "postgresql://postgres_user:placeholder_password@localhost:5432/postgres_db"
# )
# DATABASE_URL = environ.get("DATABASE_URL", default_db_url)
engine = AsyncEngine(create_engine(DB_URL, echo=True, future=True))


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
