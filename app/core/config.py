from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # 1. Database Credentials
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # 2. Connection Logic
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DATABASE_URL: str

    # 3. Security (Lawful Data Protection)
    PRIMARY_SECRET_KEY: str
    SECONDARY_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # 4. Flutterwave Webhook/Payment Security
    # Note: We use the name from your .env
    FLW_SECRET_HASH: str

    # Tells Pydantic to read your existing .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()