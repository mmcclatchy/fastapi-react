from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from utils.auth import Token, authenticate_account, create_access_token
from utils.settings import settings


router = APIRouter(prefix="")


@router.get("/health")
def health_check():
    return {"message": "Ok"}


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    account = await authenticate_account(
        session=session, username=form_data.username, password=form_data.password
    )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": account.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
