from fastapi import Depends, FastAPI, HTTPException, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import get_session, init_db
from db.models.user import User, UserCreate, UserUpdate


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
def health_check():
    return {"message": "Good to go"}


@app.get("/users", response_model=list[User])
async def get_users(session: AsyncSession = Depends(get_session)) -> list[User]:
    return await User.get_all_where(session, [])


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)) -> User:
    user = await User.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=User)
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_session)
) -> User:
    return await User(name=user.name, email=user.email).create(session)


@app.patch("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int, user_update: UserUpdate, session: AsyncSession = Depends(get_session)
) -> User:
    user = await User.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await user.update(session, user_update)
    return user


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    user = await User.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete(session)
    return Response(status_code=204)
