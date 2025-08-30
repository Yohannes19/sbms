from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Postgres DSN — override via .env or environment
    DATABASE_URL: str = "postgresql+psycopg2://postgres:Sennahoy%%40321@localhost:5432/smart_bms"
    DEBUG: bool = False
    # optional: connection pool / timeout tuning
    SQL_ECHO: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()