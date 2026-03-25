from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://conduit:conduit@localhost:5432/conduit"
    redis_url: str = "redis://localhost:6379/0"

    @model_validator(mode="after")
    def fix_database_url(self):
        """Render provides postgresql:// but asyncpg needs postgresql+asyncpg://"""
        url = self.database_url
        if url.startswith("postgres://"):
            self.database_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            self.database_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self

    # Security
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Meta
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_verify_token: str = "conduit-verify-token"
    meta_page_access_token: str = ""

    # OAuth login (ScoopOS-Conduit user authentication)
    google_client_id: str = ""
    google_client_secret: str = ""
    facebook_client_id: str = ""
    facebook_client_secret: str = ""

    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@yourdomain.com"

    # GoHighLevel
    ghl_api_key: str = ""
    ghl_location_id: str = ""

    # App
    app_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
