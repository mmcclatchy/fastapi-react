from sqlalchemy.orm import Query
from sqlalchemy.sql.expression import BinaryExpression
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


class TableModel(SQLModel):
    def __init_subclass__(cls, **kwargs) -> None:
        return super().__init_subclass__(**kwargs)

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int) -> SQLModel:
        statement = select(cls).where(cls.id == id)
        results = await session.exec(statement)
        model = results.one_or_none()
        return model

    @classmethod
    async def get_all_where(
        cls, session: AsyncSession, filters: list[BinaryExpression]
    ) -> list[SQLModel]:
        results = await session.exec(select(cls).where(*filters))
        models = results.all()
        return models

    @classmethod
    async def get_one_where(
        cls, session: AsyncSession, filters: list[BinaryExpression]
    ) -> SQLModel | None:
        statement: Query = session.exec(select(cls).where(*filters))
        model = await statement.one_or_none()
        return model

    async def create(self, session: AsyncSession) -> SQLModel:
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    async def update(self, session: AsyncSession, update_model: SQLModel) -> None:
        update_data = update_model.dict(exclude_unset=True)
        for key, val in update_data.items():
            setattr(self, key, val)
        session.add(self)
        await session.commit()
        await session.refresh(self)

    async def delete(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()
