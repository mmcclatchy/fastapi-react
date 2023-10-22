import pytest_asyncio

from db.models.user import User


@pytest_asyncio.fixture()
async def user(session) -> User:
    return await User(username="auth0|johndoe", name="John Doe", email="john.doe@email.com").create(
        session
    )


@pytest_asyncio.fixture()
async def users(session, user: User) -> tuple[User, User]:
    jane = await User(
        username="auth0|janedoe", name="Jane Smith", email="jane.smith@email.com"
    ).create(session)
    return user, jane
