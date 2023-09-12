from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from db.models.table_model import TableModel


class Account(TableModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(max_length=100, unique=True)
    email: str = Field(max_length=254)


class AccountCreate(SQLModel):
    username: str
    email: EmailStr


class AccountUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
