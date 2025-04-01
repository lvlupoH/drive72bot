import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config:
    """Конфигурация приложения с валидацией параметров"""
    
    # Обязательные параметры
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    DATABASE_URL = os.getenv("DATABASE_URL", "drive72.db")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    
    # Опциональные параметры с дефолтами
    PORT = int(os.getenv("PORT", 10000))
    ENV = os.getenv("ENV", "production")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

    @classmethod
    def validate(cls):
        """Проверка обязательных параметров"""
        missing = []
        required_vars = [
            "TELEGRAM_TOKEN",
            "ADMIN_ID",
            "EMAIL_USER",
            "EMAIL_PASSWORD",
            "ADMIN_EMAIL"
        ]

        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            error_msg = (
                "⛔ Отсутствуют обязательные переменные окружения:\n"
                f"{', '.join(missing)}\n"
                "Проверьте .env файл или системные переменные"
            )
            print(error_msg)
            sys.exit(1)

        # Дополнительные проверки
        if cls.ENV not in ("development", "production"):
            print("❌ Недопустимое значение ENV. Допустимые: development/production")
            sys.exit(1)

# Проверка конфигурации при импорте
Config.validate()
