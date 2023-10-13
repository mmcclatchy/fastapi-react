from passlib.context import CryptContext
from pydantic import EmailStr, Field
from sqlmodel import Field, SQLModel

from db.models.table_model import TableModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccountCreate(SQLModel):
    username: str
    email: EmailStr


class AccountUpdate(SQLModel):
    username: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)


class AccountResponse(AccountCreate):
    id: int
    disabled: bool


class AccountJWT(AccountCreate):
    sub: str
    disabled: bool = Field(default=False)


class Account(TableModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(
        max_length=100,
        nullable=False,
        unique=True,
    )
    email: str = Field(max_length=254)
    disabled: bool = Field(default=False)
    hashed_password: str = Field(max_length=72, nullable=True)
    external_oauth: bool = Field(default=False)

    @property
    def password(self) -> str:
        return "Password Redacted"

    @password.setter
    def password(self, unencrypted_password: str) -> None:
        self.hashed_password = pwd_context.hash(unencrypted_password)

    def verify_password(self, attempted_password: str) -> bool:
        return pwd_context.verify(attempted_password, self.hashed_password)

    def jwt(self) -> AccountJWT:
        return AccountJWT(sub=self.id, **self.dict())
