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
    SCHOOL_ADDRESS = os.getenv("SCHOOL_ADDRESS", "ул. Примерная, 123")
    
    @classmethod
    def validate(cls):
        required_vars = ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_ID"]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            sys.exit(f"Отсутствуют переменные окружения: {', '.join(missing)}")

Config.validate()