from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


class AppModel(SQLModel):
    @classmethod
    async def get(cls, session: AsyncSession, id: int) -> SQLModel:
        statement = select(cls).where(cls.id == id)
        results = await session.exec(statement)
        model = results.one_or_none()
        return model

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[SQLModel]:
        results = await session.exec(select(cls))
        models = results.all()
        return models

    async def create(self, session: AsyncSession) -> SQLModel:
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self
