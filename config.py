import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config:
    """Класс для работы с конфигурацией приложения"""
    
    # Обязательные параметры
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Опциональные параметры с дефолтными значениями
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    PORT = int(os.getenv("PORT", 10000))

    @classmethod
    def validate(cls):
        """Проверка наличия обязательных переменных"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN")
            
        if not cls.ADMIN_ID:
            errors.append("ADMIN_ID")
            
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL")

        if errors:
            print(f"❌ Отсутствуют обязательные переменные: {', '.join(errors)}")
            sys.exit(1)

# Проверка конфигурации при импорте
Config.validate()
