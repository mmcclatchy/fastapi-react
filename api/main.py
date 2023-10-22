from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1_router import V1Router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(V1Router)


@app.get("/health")
def health_check():
    return {"message": "Health Check Successful"}
