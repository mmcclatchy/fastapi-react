from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from db.models.account import (
    Account,
    AccountCreate,
    AccountJWT,
    AccountResponse,
    AccountUpdate,
)
from utils.auth import Authenticator


router = APIRouter(prefix="/accounts")


@router.get("", response_model=list[AccountResponse])
async def get_accounts(session: AsyncSession = Depends(get_session)) -> list[Account]:
    return await Account.get_all_where(session, [])


@router.get("/me", response_model=AccountJWT)
async def get_current_account(
    jwt_data: AccountJWT = Depends(Authenticator.decode_token),
) -> AccountJWT:
    return jwt_data


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, session: AsyncSession = Depends(get_session)) -> Account:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    account: AccountCreate, session: AsyncSession = Depends(get_session)
) -> Account:
    try:
        return await Account(**account.dict()).create(session)
    except IntegrityError as e:
        if 'violates unique constraint "account_username_key"' in e.args[0]:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Username unavailable")
        raise


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    session: AsyncSession = Depends(get_session),
) -> Account:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    await account.update(session, account_update)
    return account


@router.delete("/{account_id}", status_code=204)
async def delete_account(account_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    await account.delete(session)
