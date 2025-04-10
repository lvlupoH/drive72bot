import os
from dotenv import load_dotenv
import sys
import bcrypt

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    CDN_UPLOAD_URL = os.getenv("CDN_UPLOAD_URL")
    CDN_API_KEY = os.getenv("CDN_API_KEY")
    ADMIN_HASH = bcrypt.hashpw(os.getenv("ADMIN_PASSWORD").encode(), bcrypt.gensalt())  # Пароль задается отдельно

    @staticmethod
    def validate():
        required = ["TELEGRAM_TOKEN", "DATABASE_URL"]
        missing = [var for var in required if not getattr(Config, var)]
        if missing:
            sys.exit(f"Missing env vars: {missing}")

Config.validate()
