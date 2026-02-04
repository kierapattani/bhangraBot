import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Whitelist
    ALLOWED_EMAILS: list[str] = [
        email.strip()
        for email in os.getenv("ALLOWED_EMAILS", "").split(",")
        if email.strip()
    ]

    # App
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MESSAGES_FILE: Path = DATA_DIR / "selfbot_scheduled_messages.json"


settings = Settings()
