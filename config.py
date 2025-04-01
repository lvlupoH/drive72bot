import os
import sys
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Обязательные параметры
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Опциональные параметры
    ENV = os.getenv("ENV", "production")       # Режим работы: development/production
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") # Уровень логирования
    PORT = int(os.getenv("PORT", 10000))       # Порт для вебхуков
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") # Базовый URL для вебхуков

    @classmethod
    def validate(cls):
        """Проверка обязательных переменных"""
        missing = []
        
        if not cls.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_TOKEN")
            
        if not cls.ADMIN_ID:
            missing.append("ADMIN_ID")
            
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")

        if missing:
            raise ValueError(
                f"Отсутствуют обязательные переменные: {', '.join(missing)}"
            )

# Проверка при импорте модуля
try:
    Config.validate()
except ValueError as e:
    print(f"Ошибка конфигурации: {str(e)}")
    sys.exit(1)
