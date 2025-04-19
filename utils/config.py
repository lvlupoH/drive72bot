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
    SCHOOL_ADDRESS = os.getenv(
        "SCHOOL_ADDRESS",
        "рп. Боровский, ул. Набережная д.55, офис 105\nг. Тюмень, ул. Николая Гондатти д.7/2, офис 210"
    )

    @classmethod
    def validate(cls):
        required = ["TELEGRAM_TOKEN", "DATABASE_URL", "EMAIL_USER", "EMAIL_PASSWORD", "ADMIN_EMAIL", "ADMIN_ID", "WEBHOOK_URL"]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            sys.exit(f"Ошибка: Отсутствуют переменные окружения: {', '.join(missing)}")

Config.validate()