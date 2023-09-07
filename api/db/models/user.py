from sqlmodel import Field, SQLModel

from db.models.table_model import TableModel


class User(TableModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


class UserCreate(SQLModel):
    name: str
    email: str


class UserUpdate(SQLModel):
    name: str | None
    email: str | None
