from fastapi import FastAPI

from api import accounts


app = FastAPI()


@app.get("/")
def health_check():
    return {"message": "Health Check"}


app.include_router(accounts.router)
