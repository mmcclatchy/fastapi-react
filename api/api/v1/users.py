from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from db.models.user import User
from utils.auth import (
    Auth0UserData,
    get_auth0_user_data,
    get_db_user,
    require_admin,
    require_user,
)


router = APIRouter(prefix="/users")


@router.get("/me", response_model=User, dependencies=[Depends(require_user)])
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    auth0_user_data: Auth0UserData = Depends(get_auth0_user_data),
):
    return await get_db_user(session, auth0_user_data)


@router.get("", response_model=list[User], dependencies=[Depends(require_admin)])
async def get_users(session: AsyncSession = Depends(get_session)) -> list[User]:
    return await User.get_all_where(session, [])


@router.get("/{user_id}", response_model=User, dependencies=[Depends(require_admin)])
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await User.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
