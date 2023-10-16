from secrets import token_urlsafe
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from utils.auth import Authenticator, Token


router = APIRouter(prefix="")


@router.post("/signup", response_model=Token)
async def signup(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    authenticator = Authenticator(session=session)
    account = await authenticator.create_account(form)
    return Authenticator.create_access_token(account)


@router.post("/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    authenticator = Authenticator(session=session)
    account = await authenticator.authenticate_account(form)
    return authenticator.create_access_token(account)


@router.get("/login/{provider_name}")
async def login_provider(provider_name: str, request: Request):
    request.session.clear()
    request.session["nonce"] = token_urlsafe(16)
    authenticator = Authenticator(provider_name=provider_name)
    redirect_url = await authenticator.authorize_redirect(request)
    return redirect_url


@router.get("/auth/{provider_name}", response_model=Token)
async def auth_provider(
    provider_name: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Token:
    authenticator = Authenticator(session=session, provider_name=provider_name)
    return await authenticator.create_access_token_via_provider(request)
