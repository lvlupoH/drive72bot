import os
import sys
from dotenv import load_dotenv
import bcrypt

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    CDN_URL = os.getenv("CDN_URL", "https://default-cdn.com")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_PASSWORD_HASH = bcrypt.hashpw(os.getenv("ADMIN_PASSWORD").encode(), bcrypt.gensalt()) if os.getenv("ADMIN_PASSWORD") else None

    @classmethod
    def validate(cls):
        required = ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_ID"]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            sys.exit(f"Missing env vars: {missing}")

Config.validate()