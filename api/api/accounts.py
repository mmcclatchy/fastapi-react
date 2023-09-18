from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from db.models.account import Account, AccountCreate, AccountUpdate


router = APIRouter(prefix="/accounts")


@router.get("", response_model=list[Account])
async def get_accounts(session: AsyncSession = Depends(get_session)) -> list[Account]:
    return await Account.get_all_where(session, [])


@router.get("/{account_id}", response_model=Account)
async def get_account(
    account_id: int, session: AsyncSession = Depends(get_session)
) -> Account:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("", response_model=Account, status_code=201)
async def create_account(
    account: AccountCreate, session: AsyncSession = Depends(get_session)
) -> Account:
    return await Account(**account.dict()).create(session)


@router.patch("/{account_id}", response_model=Account)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    session: AsyncSession = Depends(get_session),
) -> Account:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    await account.update(session, account_update)
    return account


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    await account.delete(session)


@router.patch("/test/{account_id}", response_model=Account)
async def test(
    account_id: int,
    account_update: AccountUpdate,
    session: AsyncSession = Depends(get_session),
) -> Account:
    account = await Account.get_by_id(session, account_id)
    await account.update(session, account_update)
    return account
