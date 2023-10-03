from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from db.models.account import Account
from utils.settings import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


def decode_token(token: Annotated[dict[str, Any], Depends(oauth2_scheme)]) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception


async def get_active_account(
    token_data: Annotated[TokenData, Depends(decode_token)],
    session: AsyncSession = Depends(get_session),
) -> Account:
    account = await Account.get_one_where(
        session, [Account.username == token_data.username]
    )
    if not account:
        raise credentials_exception
    if account.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return account


async def authenticate_account(session: AsyncSession, username: str, password: str):
    account = await Account.get_one_where(session, [Account.username == username])
    if not account or not account.verify_password(password):
        raise credentials_exception
    return account


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
