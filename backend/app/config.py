from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/address_sync.db"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    # mock UIDAI: OTP is returned in the API response instead of sent via SMS
    dev_mode: bool = True

    webhook_base_url: str = "http://127.0.0.1:8000"
    worker_poll_seconds: float = 1.5
    webhook_max_attempts: int = 3
    webhook_timeout_seconds: float = 10.0


settings = Settings()
