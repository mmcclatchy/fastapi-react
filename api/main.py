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
    return await User.get_all(session)


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    return await User.get(session, user_id)


@app.post("/users", response_model=User)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    return await User(name=user.name, email=user.email).create(session)
