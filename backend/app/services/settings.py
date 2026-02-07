import logging
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, model_validator
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    JWT_ALGORITHM: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    OTP_VALIDITY_MINUTES: Optional[int] = None
    OTP_LENGTH: Optional[int] = None
    DATABASE_URL: Optional[str] = None
    CORS_ORIGINS: Optional[List[str]] = None
    NOTIFICATION_MODE: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
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
            raise ValidationError("Database Not Configured!")
    
    def verifyNotificationConfiguration(self):
        if self.NOTIFICATION_MODE is not None and self.NOTIFICATION_MODE.lower() == "email":
            self.verifySmtpConfiguration()

    def verifySmtpConfiguration(self):
        missing = []
        if self.SMTP_HOST is None:
            missing.append("SMTP_SERVER")
        if self.SMTP_USER is None:
            missing.append("SMTP_USER")
        if self.SMTP_PASSWORD is None:
            missing.append("SMTP_PASSWORD")
        if self.SMTP_FROM is None:
            missing.append("SENDER_EMAIL")

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