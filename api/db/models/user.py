# from passlib.context import CryptContext
from pydantic import Field
from sqlmodel import Field

from db.models.table_model import TableModel


class User(TableModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(max_length=254, nullable=False)
    name: str = Field(max_length=254, nullable=False)
    username: str = Field(
        max_length=100,
        nullable=False,
        unique=True,
        index=True,
    )
