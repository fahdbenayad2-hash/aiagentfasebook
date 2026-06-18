from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Facebook / Instagram
    FACEBOOK_APP_SECRET: str
    FACEBOOK_PAGE_ACCESS_TOKEN: str
    FACEBOOK_VERIFY_TOKEN: str
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_STAFF_CHAT_ID: str

    # App
    APP_SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///data/shop.db"
    LOG_LEVEL: str = "INFO"

    # Admin Auth
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # Rate Limiting
    RATE_LIMIT_WEBHOOK: str = "10/minute"
    RATE_LIMIT_ADMIN: str = "30/minute"

    # Conversation
    CONVERSATION_TIMEOUT_MINUTES: int = 30

    # Groq Retry
    GROQ_MAX_RETRIES: int = 3
    GROQ_RETRY_DELAY: float = 1.0

    # Caching
    PRODUCT_CACHE_TTL_SECONDS: int = 60

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
