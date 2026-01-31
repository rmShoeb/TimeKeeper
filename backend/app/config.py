import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, model_validator
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OTP_VALIDITY_MINUTES: int = 2
    OTP_LENGTH: int = 6
    DATABASE_URL: str = ""
    JWT_SECRET_KEY: str = ""
    CORS_ORIGINS: List[str] = []
    NOTIFICATION_MODE: str = ""
    SCHEDULER_TIMEZONE: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode='after')
    def check_notification_config(self) -> 'Settings':
        if len(self.DATABASE_URL) == 0:
            raise ValidationError("Database Not Configured!")
        if self.NOTIFICATION_MODE.lower() == "email":
            missing = []
            if len(self.SMTP_HOST) == 0:
                missing.append("SMTP_SERVER")
            if len(self.SMTP_USER) == 0:
                missing.append("SMTP_USER")
            if len(self.SMTP_PASSWORD) == 0:
                missing.append("SMTP_PASSWORD")
            if len(self.SMTP_FROM) == 0:
                missing.append("SENDER_EMAIL")
            
            if missing:
                raise ValidationError(f"Notification mode is SMTP, but the following configurations are missing: {', '.join(missing)}")
        return self


@lru_cache
def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        print("\n" + "="*60)
        print("CONFIGURATION ERROR: The application failed to start.")
        print("="*60)
        for error in e.errors():
            # Get field name
            field = error['loc'][0]
            msg = error['msg']
            print(f"{field}: {msg}")
        
        print("="*60 + "\n")
        # Exit the application immediately
        sys.exit(1)

settings = get_settings()