import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    @classmethod
    def validate(cls):
        missing = []
        if not cls.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_TOKEN")
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        if missing:
            print(f"Ошибка: Отсутствуют переменные: {', '.join(missing)}")
            sys.exit(1)

Config.validate()