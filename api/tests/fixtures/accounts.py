import pytest_asyncio

from db.models.account import Account


@pytest_asyncio.fixture()
async def account(session) -> Account:
    return await Account(username="John Doe", email="john.doe@email.com").create(session)


@pytest_asyncio.fixture()
async def accounts(session, account: Account) -> tuple[Account, Account]:
    jane = await Account(username="Jane Smith", email="jane.smith@email.com").create(session)
    return account, jane
