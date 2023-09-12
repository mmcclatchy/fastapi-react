from os import environ


ENV = environ.get("ENV", "dev")
DB_URL = environ.get(
    "DATABASE_URL", "postgresql+asyncpg://myuser:mypassword@db:5432/mydb"
)
TEST_DB_URL = "postgresql+asyncpg://myuser:mypassword@test_db:5433/test-db"
API_BASE_URL = environ.get("API_BASE_URL", "http://0.0.0.0:8080")
API_V1_PREFIX = f"{API_BASE_URL}/v1"
