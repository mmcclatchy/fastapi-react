from os import environ

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    env: str = Field("dev", env="ENV")
    db_url: str = Field(
        "postgresql+asyncpg://myuser:mypassword@db:5432/mydb", env="DB_URL"
    )
    test_db_url: str = Field(
        "postgresql+asyncpg://myuser:mypassword@test_db:5432/test-db", env="TEST_DB_URL"
    )
    api_base_url: str = Field("http://0.0.0.0:8080", env="API_BASE_URL")
    access_token_expire_minutes = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    algorithm: str
    jwt_secret_key: str
    google_client_id: str
    google_client_secret: str

    class Config:
        env_file = ".env.dev" if environ.get("ENV", "dev") == "dev" else None


settings = Settings()
