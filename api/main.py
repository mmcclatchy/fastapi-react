import logging

from fastapi import Depends, FastAPI
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session, init_db
from db.models.user import User, UserCreate

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
def health_check():
    return {"message": "Good to go"}


@app.get("/users", response_model=list[User])
async def get_users(session: AsyncSession = Depends(get_session)):
    users: list[User] = await User.get_all(session)
    return users


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user: User = await User.get(session, user_id)
    logging.info(f"User Name: {user.name}, User Email: {user.email}")
    return user


@app.post("/users", response_model=User)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    db_user: User = User(name=user.name, email=user.email)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
