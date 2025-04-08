import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))

    @classmethod
    def validate(cls):
        required = ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_ID", "ADMIN_PASSWORD"]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            print(f"Missing variables: {', '.join(missing)}")
            sys.exit(1)

Config.validate()