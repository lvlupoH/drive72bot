# config.py
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    
    @classmethod
    def validate(cls):
        missing = []
        for var in ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_ID"]:
            if not getattr(cls, var):
                missing.append(var)
        if missing:
            print(f"Отсутствуют переменные: {', '.join(missing)}")
            sys.exit(1)

Config.validate()