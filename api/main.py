from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api import auth
from api.v1_router import V1Router
from utils.settings import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
)

app.include_router(auth.router)
app.include_router(V1Router)


@app.get("/health")
def health_check():
    return {"message": "Health Check Successful"}
