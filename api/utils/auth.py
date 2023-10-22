from fastapi import Depends, HTTPException, status
from fastapi_auth0 import Auth0, Auth0User
from httpx import AsyncClient
from pydantic import BaseModel, EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession

from db.models.user import User
from utils.settings import settings


auth0 = Auth0(
    domain=settings.auth0_domain,
    api_audience=settings.auth0_audience,
    scopes={"user:basic": "Basic User", "user:admin": "Admin User"},
)


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


class Auth0UserData(BaseModel):
    sub: str
    name: str
    email: EmailStr


class PermissionsValidator:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, auth0_user: Auth0User = Depends(auth0.get_user)) -> None:
        token_permissions_set = set(auth0_user.permissions)
        required_permissions_set = set(self.required_permissions)

        if not required_permissions_set.issubset(token_permissions_set):
            raise PermissionDeniedException


require_user = PermissionsValidator(["user:basic"])
require_admin = PermissionsValidator(["user:admin"])


async def get_auth0_user_data(token=Depends(auth0.authcode_scheme)) -> Auth0UserData:
    async with AsyncClient() as client:
        response = await client.get(
            settings.auth0_user_info_endpoint,
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        user_data = response.json()
        return Auth0UserData(**user_data)


async def get_db_user(session: AsyncSession, auth0_user_data: Auth0UserData) -> User:
    user = await User.get_one_where(session, [User.username == auth0_user_data.sub])
    if user is None:
        user = await User(
            username=auth0_user_data.sub, email=auth0_user_data.email, name=auth0_user_data.name
        ).create(session)
    return user
