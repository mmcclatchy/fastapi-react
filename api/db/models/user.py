from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


class UserCreate(SQLModel):
    name: str
    email: str
