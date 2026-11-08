import logging
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, model_validator
from functools import lru_cache
from typing import List, Optional, Literal

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    LOG_DIR: str = "logs"
    JWT_ALGORITHM: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    OTP_VALIDITY_MINUTES: Optional[int] = None
    OTP_LENGTH: Optional[int] = None
    DATABASE_URL: Optional[str] = None
    CORS_ORIGINS: Optional[List[str]] = None
    NOTIFICATION_MODE: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_FROM: Optional[str] = None
    SCHEDULER_TIMEZONE: Optional[str] = None
    LOGGER_TOKEN: Optional[str] = None
    LOGGER_HOST: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode='after')
    def check_notification_config(self) -> 'Settings':
        self.verifyCrucialconfiguration()
        self.verifyNotificationConfiguration()
        return self
    
    def verifyCrucialconfiguration(self):
        if self.DATABASE_URL is None:
            raise ValueError("Database Not Configured!")
        if self.ENVIRONMENT == "prod":
            if not self.LOGGER_TOKEN:
                raise ValueError("LOGGER_TOKEN (Better Stack ingestion token) is required when ENVIRONMENT is 'prod'")
    
    def verifyNotificationConfiguration(self):
        if self.NOTIFICATION_MODE is not None and self.NOTIFICATION_MODE.lower() == "email":
            self.verifySmtpConfiguration()

    def verifySmtpConfiguration(self):
        missing = []
        if not self.SMTP_HOST:
            missing.append("SMTP_HOST")
        if not self.SMTP_PORT:
            missing.append("SMTP_PORT")
        if not self.SMTP_USER:
            missing.append("SMTP_USER")
        if not self.SMTP_PASSWORD:
            missing.append("SMTP_PASSWORD")
        if not self.SMTP_FROM:
            missing.append("SMTP_FROM")

        if missing:
            raise ValueError(f"Notification mode is SMTP, but the following configurations are missing: {', '.join(missing)}")


@lru_cache
def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        print("CONFIGURATION ERROR: The application failed to start.")
        for error in e.errors():
            print(f"{error['msg']}")
        sys.exit(1)

settings = get_settings()