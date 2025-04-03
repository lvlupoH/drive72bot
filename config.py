import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))  # Render требует порт 10000

    @classmethod
    def validate(cls):
        missing = []
        for var in ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_ID", "WEBHOOK_URL"]:
            if not getattr(cls, var):
                missing.append(var)
        if missing:
            print(f"Missing: {', '.join(missing)}")
            sys.exit(1)

Config.validate()