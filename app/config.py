import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENVIRONMENT = os.environ.get("FLASK_ENV", "development")

    if ENVIRONMENT == "production":
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/leetcode_analytics",
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get("DEV_DATABASE_URI")
            or f"sqlite:///{BASE_DIR / 'database' / 'dev.db'}"
        )

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Example: enable secure cookies in production via env
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    LEETCODE_BASE_URL = "[leetcode.com](https://leetcode.com)"
    LEETCODE_GRAPHQL_URL = "[leetcode.com](https://leetcode.com/graphql)"  # used by service layer
