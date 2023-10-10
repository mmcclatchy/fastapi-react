from datetime import datetime, timedelta
from typing import Annotated, Any, Callable

import google.auth.transport.requests
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from httpx import AsyncClient
from jose import JWTError, jwt
from pydantic import BaseModel, Field, ValidationError
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
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    oauth = OAuth()
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )
    # oauth.register(
    #     name="github",
    #     authorize_url="https://github.com/login/oauth/authorize",
    #     access_token_url="https://github.com/login/oauth/access_token",
    #     client_kwargs={"scope": "user:email"},
    #     client_id=settings.github_client_id,
    #     client_secret=settings.github_client_secret,
    # )
    oauth.register(
        "discord",
        authorize_url="https://discord.com/oauth2/authorize",
        access_token_url="https://discord.com/api/oauth2/token",
        client_kwargs={"scope": "identify email"},
        client_id=settings.discord_client_id,
        client_secret=settings.discord_client_secret,
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
        if self.provider_name not in {"google", "discord", "github"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Oauth provider",
            )

        self.provider = getattr(self.oauth, provider_name)
        self.get_user_data = getattr(self, f"get_{provider_name}_user_data")
        self.redirect_uri = f"/auth/{provider_name}"

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

    async def authenticate_account(self, username: str, password: str) -> Account:
        account = await Account.get_one_where(self.session, [Account.username == username])
        if not account or not account.verify_password(password):
            logger.error("CredentialsException: could not verify password")
            raise self.CredentialsException
        return account

    async def get_current_account(
        self, jwt_data: Annotated[AccountJWT, Depends(decode_token)]
    ) -> Account:
        account = await Account.get_one_where(self.session, [Account.username == jwt_data.username])
        if not account:
            logger.error(f"CredentialsException: no matching account for {jwt_data.username}")
            raise self.CredentialsException
        if account.disabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        return account

    async def authorize_redirect(self, request: Request):
        redirect_url = f"{settings.api_base_url}/auth/{self.provider_name}"
        nonce = request.session.get("nonce")
        print(f"============\n\Auth Redirect Nonce:\n{nonce}\n\n============")
        return await self.provider.authorize_redirect(request, redirect_url, nonce=nonce)

    async def create_access_token_via_provider(self, request: Request) -> Token:
        try:
            provider_token = await self.provider.authorize_access_token(request)
        except OAuthError as error:
            logger.error(f"OAuthError: {error.error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.error
            )

        user_data = await self.get_user_data(provider_token, request)
        account = await Account.get_one_where(self.session, [Account.email == user_data.email])
        if account is None:
            account = await Account(
                username=user_data.email, email=user_data.email, external_oauth=True
            ).create(self.session)
        return self.create_access_token(account)

    async def get_google_user_data(self, token: dict[str, Any]) -> OauthData:
        oauth_jwt = token["id_token"]
        google_req = google.auth.transport.requests.Request()
        id_data = id_token.verify_oauth2_token(oauth_jwt, google_req, settings.google_client_id)
        if id_data["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.error("GoogleOAuthError: invalid iss")
            raise self.CredentialsException
        return OauthData(**id_data)

    @classmethod
    def get_provider_identity_function(cls, provider_user_url: str) -> Callable:
        async def _get_user_data(token: Token) -> OauthData:
            headers = {"Authorization": f"Bearer {token}"}
            async with AsyncClient() as client:
                response = await client.get(provider_user_url, headers=headers)

                if response.status_code != 200:
                    logger.error(
                        f"Oauth Client Error - status: {response.status_code}, "
                        + f"provider_url: {provider_user_url}"
                    )
                    raise cls.CredentialsException

                user_data = response.json()
                return OauthData(**user_data)

        return _get_user_data

    # @classmethod
    # async def get_github_user_data(cls, token: Token) -> OauthData:
    #     github_url = "https://api.github.com/user"
    #     _get_github_user_data = cls.get_provider_identity_function(github_url)
    #     return await _get_github_user_data(token)

    @classmethod
    async def get_discord_user_data(cls, token: dict[str, Any]) -> OauthData:
        discord_url = "https://discord.com/api/users/@me"
        get_discord_identity = cls.get_provider_identity_function(discord_url)
        return await get_discord_identity(token["access_token"])
