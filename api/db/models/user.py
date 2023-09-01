from sqlmodel import Field, SQLModel

from db.models.app_model import AppModel


class User(AppModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


class UserCreate(SQLModel):
    name: str
    email: str
