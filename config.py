import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config:
    """Конфигурация приложения с валидацией обязательных параметров"""
    
    # Обязательные параметры (должны быть указаны в .env)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # ID администратора в Telegram
    DATABASE_URL = os.getenv("DATABASE_URL")  # URL подключения к PostgreSQL
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")    # Полный URL вебхука
    
    # Опциональные параметры с дефолтными значениями
    PORT = int(os.getenv("PORT", 10000))      # Порт для вебхука (по умолчанию 10000)
    ENV = os.getenv("ENV", "production")      # Режим работы: production/development
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")# Уровень логирования

    @classmethod
    def validate(cls):
        """Проверка наличия обязательных переменных окружения"""
        missing = []
        
        if not cls.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_TOKEN")
            
        if not cls.ADMIN_ID:
            missing.append("ADMIN_ID (должен быть числовым ID)")
            
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
            
        if not cls.WEBHOOK_URL:
            missing.append("WEBHOOK_URL")

        if missing:
            error_msg = "❌ Отсутствуют обязательные переменные в .env:\n" + "\n".join(missing)
            print(error_msg)
            sys.exit(1)

# Проверка конфигурации при импорте модуля
Config.validate()
