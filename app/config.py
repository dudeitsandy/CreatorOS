from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/creatorosdb"
    redis_url: str = "redis://localhost:6379/0"
    together_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""   # Set in Telegram setWebhook call; used to verify inbound requests
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    encryption_key: str = ""
    dashboard_token: str = ""           # Bearer token required to access /webhooks/dashboard
    allowed_origins: str = ""           # Comma-separated CORS origins; empty = localhost only
    environment: str = "development"    # "production" enables stricter settings

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
