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
    username: str = Field(max_length=100, unique=True)
    email: str = Field(min_length=6, max_length=254)
    _disabled: bool = Field(default=False)
    _hashed_password: str = Field(min_length=44, max_length=72)
    _external_oauth: bool = Field(default=False)

    @property
    def disabled(self):
        # TODO: DELETE THIS

        return False

    @property
    def password(self) -> str:
        # return self._hashed_password
        return "faked-hash+test"

    @password.setter
    def password(self, unencrypted_password: str) -> None:
        # self._hashed_password = pwd_context.hash(unencrypted_password)
        setattr(self, "_fake_password", f"faked-hash+{unencrypted_password}")

    def verify_password(self, attempted_password: str) -> bool:
        # return self._hashed_password == pwd_context.hash(attempted_password)
        return self.password == f"faked-hash+{attempted_password}"

    def jwt(self) -> AccountJWT:
        return AccountJWT(sub=self.id, **self.dict())
