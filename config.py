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
    ENV = os.getenv("ENV", "production")

    @classmethod
    def validate(cls):
        missing = []
        for var in ["TELEGRAM_TOKEN", "DATABASE_URL", "EMAIL_USER", 
                   "EMAIL_PASSWORD", "ADMIN_EMAIL", "ADMIN_ID", 
                   "WEBHOOK_URL"]:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            print(f"Ошибка: Отсутствуют переменные окружения: {', '.join(missing)}")
            sys.exit(1)

Config.validate()
