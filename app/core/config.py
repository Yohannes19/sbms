from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Postgres DSN — override via .env or environment
    DATABASE_URL: str
    DEBUG: bool = False
    # optional: connection pool / timeout tuning
    SQL_ECHO: bool = False

    # auth
    SECRET_KEY: str = Field("change-me-to-a-secure-random-string", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()