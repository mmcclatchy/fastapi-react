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

    auth0_algorithm: str
    auth0_audience: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_domain: str

    @property
    def auth0_issuer(self):
        return f"https://{self.auth0_domain}/"

    @property
    def auth0_user_info_endpoint(self):
        return f"{self.auth0_issuer}userinfo"

    class Config:
        env_file = ".env.dev" if environ.get("ENV", "dev") == "dev" else None


settings = Settings()
