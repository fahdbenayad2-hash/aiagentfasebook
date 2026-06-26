from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Facebook (new names)
    FB_PAGE_ACCESS_TOKEN: str = ""
    FB_VERIFY_TOKEN: str = "maria_verify_2026"
    FB_APP_SECRET: str = ""
    FB_APP_ID: str = ""
    FB_REDIRECT_URI: str = ""
    FB_API_VERSION: str = "v18.0"
    TOKEN_ENCRYPTION_KEY: str = ""
    # Facebook (legacy names - for backwards compat)
    FACEBOOK_PAGE_ACCESS_TOKEN: str = ""
    FACEBOOK_VERIFY_TOKEN: str = ""
    FACEBOOK_APP_SECRET: str = ""
    IG_BUSINESS_ACCOUNT_ID: str = ""

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    GROQ_MODEL_MAIN: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_CLASSIFIER: str = "llama3-8b-8192"
    GROQ_MAX_TOKENS: int = 512
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MAX_RETRIES: int = 2
    GROQ_RETRY_DELAY: float = 1.0

    # Session
    SESSION_BACKEND: str = "sqlite"
    SESSION_TTL_MINUTES: int = 30
    REDIS_URL: str = ""
    SESSION_DB_PATH: str = "data/sessions.db"
    SESSION_EXPIRY_HOURS: int = 72
    MAX_CONVERSATION_HISTORY: int = 50

    # Escalation
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_CHAT_ID: str = ""
    TELEGRAM_STAFF_CHAT_ID: str = ""
    TELEGRAM_ADMIN_CHAT_IDS: str = ""

    # Feature Flags
    FAHD_ENABLED: bool = True
    FAHD_MAX_MESSAGES_PER_SESSION: int = 50
    FAHD_COOLDOWN_AFTER_ESCALATION_MINUTES: int = 60

    # Auth
    APP_SECRET_KEY: str = "change-me-in-production"

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # Database
    DATABASE_URL: str = "sqlite:///data/shop.db"

    # Rate limiting
    RATE_LIMIT_WEBHOOK: str = "10/minute"
    RATE_LIMIT_ADMIN: str = "30/minute"

    # Conversation
    CONVERSATION_TIMEOUT_MINUTES: int = 30
    PRODUCT_CACHE_TTL_SECONDS: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # Feature Flags
    FEATURE_INTENT_CLASSIFIER: bool = True
    FEATURE_SQLITE_SESSION: bool = True
    FEATURE_ASYNC_METRICS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


def get_settings():
    return settings
