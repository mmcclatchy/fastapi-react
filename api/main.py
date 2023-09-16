from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session
from db.models.account import Account, AccountCreate, AccountUpdate


app = FastAPI()
router = APIRouter(prefix="/v1")


@router.get("/")
def health_check():
    return {"message": "Health Check"}


@router.get("/accounts", response_model=list[Account])
async def get_accounts(session: AsyncSession = Depends(get_session)) -> list[Account]:
    return await Account.get_all_where(session, [])


@router.get("/accounts/{account_id}", response_model=Account)
async def get_account(
    account_id: int, session: AsyncSession = Depends(get_session)
) -> Account:
    account = await Account.get_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/accounts", response_model=Account, status_code=201)
async def create_account(
    account: AccountCreate, session: AsyncSession = Depends(get_session)
) -> Account:
    return await Account(**account.dict()).create(session)


@router.patch("/accounts/{account_id}", response_model=Account)
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


@router.delete("/accounts/{account_id}", status_code=204)
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


app.include_router(router)
