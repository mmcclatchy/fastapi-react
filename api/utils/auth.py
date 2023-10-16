from datetime import datetime, timedelta
from typing import Annotated, Any

import google.auth.transport.requests
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm
from google.oauth2 import id_token
from httpx import AsyncClient
from jose import JWTError, jwt
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from db.models.account import Account, AccountJWT
from utils.logging import logger
from utils.settings import settings


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


class OauthData(BaseModel):
    email: str


class JWTData(AccountJWT):
    exp: datetime


class Authenticator:
    oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token", authorizationUrl="authorize")

    oauth = OAuth()
    oauth.register(
        "discord",
        authorize_url="https://discord.com/oauth2/authorize",
        access_token_url="https://discord.com/api/oauth2/token",
        client_kwargs={"scope": "identify email"},
        client_id=settings.discord_client_id,
        client_secret=settings.discord_client_secret,
    )
    oauth.register(
        name="github",
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        client_kwargs={"scope": "user:email read:user"},
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
    )
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )

    CredentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def __init__(self, session: AsyncSession | None = None, provider_name: str | None = None):
        self.session = session

        if provider_name is None:
            return

        self.provider_name = provider_name.strip()
        if self.provider_name not in {"discord", "github", "google"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Oauth provider",
            )

        self.provider = getattr(self.oauth, provider_name)
        self.get_user_data = getattr(self, f"get_user_data_via_{provider_name}")
        self.redirect_uri = f"/auth/{provider_name}"

    async def create_account(self, form: OAuth2PasswordRequestForm) -> Account:
        try:
            account = await Account(
                username=form.username, email=form.email, password=form.password
            ).create(self.session)
        except IntegrityError as e:
            logger.error(f"SQLAlchemy IntegrityError: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Submitted credentials already exist"
            )
        return account

    async def authenticate_account(self, form: OAuth2PasswordRequestForm) -> Account:
        account = await Account.get_one_where(self.session, [Account.username == form.username])
        if not account or not account.verify_password(form.password):
            logger.error("CredentialsException: could not verify password")
            raise self.CredentialsException
        return account

    @staticmethod
    def create_access_token(account: Account, expire_in_minutes: int | None = None) -> Token:
        if expire_in_minutes is None:
            expire_in_minutes = settings.access_token_expire_minutes

        expire = datetime.utcnow() + timedelta(minutes=expire_in_minutes)
        jwt_data = JWTData(sub=account.id, **account.dict(), exp=expire)
        access_token = jwt.encode(
            jwt_data.dict(), settings.secret_key, algorithm=settings.algorithm
        )
        return Token(access_token=access_token)

    @staticmethod
    def decode_token(token: Annotated[dict[str, Any], Depends(oauth2_scheme)]) -> AccountJWT:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return AccountJWT(**payload)
        except (JWTError, ValidationError) as e:
            logger.error(f"{e.__class__.__name__}: {e}", exc_info=True)
            raise Authenticator.CredentialsException

    async def get_current_account(
        self, jwt_data: Annotated[AccountJWT, Depends(decode_token)]
    ) -> Account:
        account = await Account.get_one_where(self.session, [Account.username == jwt_data.username])
        if not account:
            logger.error(f"CredentialsException: no matching account for {jwt_data.username}")
            raise self.CredentialsException
        if account.disabled:
            logger.error(f"CredentialsException: no matching account for {jwt_data.username}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive account")
        return account

    async def authorize_redirect(self, request: Request):
        redirect_url = f"{settings.api_base_url}/auth/{self.provider_name}"
        nonce = request.session.get("nonce")
        return await self.provider.authorize_redirect(request, redirect_url, nonce=nonce)

    async def create_access_token_via_provider(self, request: Request) -> Token:
        try:
            provider_token = await self.provider.authorize_access_token(request)
        except OAuthError as error:
            logger.error(f"OAuthError: {error.error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.error
            )

        user_data = await self.get_user_data(provider_token)
        account = await Account.get_one_where(self.session, [Account.email == user_data.email])
        if account is None:
            account = await Account(
                username=user_data.email, email=user_data.email, external_oauth=True
            ).create(self.session)
        return self.create_access_token(account)

    async def get_user_data_via_google(self, token: dict[str, Any]) -> OauthData:
        oauth_jwt = token["id_token"]
        google_req = google.auth.transport.requests.Request()
        id_data = id_token.verify_oauth2_token(oauth_jwt, google_req, settings.google_client_id)
        if id_data["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.error("GoogleOAuthError: invalid iss")
            raise self.CredentialsException
        return OauthData(**id_data)

    @classmethod
    async def provider_request(cls, access_token: str, provider_url: str) -> Any:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with AsyncClient() as client:
            response = await client.get(provider_url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Oauth Client Error - status: {response.status_code}, "
                    + f"provider_url: {provider_url}"
                )
                raise cls.CredentialsException

            return response.json()

    @classmethod
    async def get_user_data_via_github(cls, token: dict[str, Any]) -> OauthData:
        access_token = token["access_token"]
        github_url = "https://api.github.com/user/emails"
        user_emails_data = await cls.provider_request(access_token, github_url)
        primary_email = [ued["email"] for ued in user_emails_data if ued["primary"] is True][0]
        return OauthData(email=primary_email)

    @classmethod
    async def get_user_data_via_discord(cls, token: dict[str, Any]) -> OauthData:
        access_token = token["access_token"]
        discord_url = "https://discord.com/api/users/@me"
        user_data = await cls.provider_request(access_token, discord_url)
        return OauthData(email=user_data["email"])
