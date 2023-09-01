from db.models.app_model import AppModel
from sqlmodel import Field, SQLModel


class User(AppModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


class UserCreate(SQLModel):
    name: str
    email: str
