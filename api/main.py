from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth
from api.v1_router import V1Router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost" "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(V1Router)
