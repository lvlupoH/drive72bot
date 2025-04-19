import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))
    SCHOOL_ADDRESS = os.getenv("SCHOOL_ADDRESS", "Адреса автошколы...")

    @classmethod
    def validate(cls):
        required = ["TELEGRAM_TOKEN", "DATABASE_URL", "EMAIL_USER", "EMAIL_PASSWORD", "ADMIN_EMAIL", "ADMIN_ID", "WEBHOOK_URL"]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            sys.exit(f"Отсутствуют переменные окружения: {', '.join(missing)}")

Config.validate()