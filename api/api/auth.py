from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from utils.auth import Authenticator, Token


router = APIRouter(prefix="")


@router.get("/health")
def health_check():
    return {"message": "Health Check Successful"}


@router.post("/token", response_model=Token)
async def auth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    authenticator = Authenticator(session=session)
    account = await authenticator.authenticate_account(
        username=form_data.username, password=form_data.password
    )
    return authenticator.create_access_token(account)


@router.get("/login/{provider_name}")
async def login_provider(provider_name: str, request: Request):
    request.session.clear()
    authenticator = Authenticator(provider_name=provider_name)
    return await authenticator.authorize_redirect(request)


@router.get("/auth/{provider_name}", response_model=Token)
async def auth_provider(
    provider_name: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Token:
    authenticator = Authenticator(session=session, provider_name=provider_name)
    return await authenticator.create_access_token_via_provider(request)
