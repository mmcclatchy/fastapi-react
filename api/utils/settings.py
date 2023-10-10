from os import environ

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    env: str = Field("dev", env="ENV")
    db_url: str = Field("postgresql+asyncpg://myuser:mypassword@db:5432/mydb", env="DB_URL")
    test_db_url: str = Field(
        "postgresql+asyncpg://myuser:mypassword@test_db:5432/test-db", env="TEST_DB_URL"
    )
    api_base_url: str = Field("http://127.0.0.1:8080", env="API_BASE_URL")
    frontend_base_url: str = Field("http://127.0.0.1:3000", env="FRONTEND_BASE_URL")
    access_token_expire_minutes = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    algorithm: str
    secret_key: str
    discord_client_id: str
    discord_client_secret: str
    github_client_id: str
    github_client_secret: str
    google_client_id: str
    google_client_secret: str

    class Config:
        env_file = ".env.dev" if environ.get("ENV", "dev") == "dev" else None


settings = Settings()
