import os
import sys
from dotenv import load_dotenv
import bcrypt

# Загрузка переменных из .env файла
load_dotenv()

class Config:
    """Класс конфигурации приложения"""
    
    # Обязательные переменные
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # Преобразуем в число
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # CDN и дополнительные настройки
    CDN_UPLOAD_URL = os.getenv("CDN_UPLOAD_URL")
    CDN_API_KEY = os.getenv("CDN_API_KEY")
    
    # Опциональные параметры с дефолтами
    PORT = int(os.getenv("PORT", 10000))  # Порт по умолчанию для Render
    ENV = os.getenv("ENV", "production")  # Режим работы: production/development
    
    # Безопасность
    ADMIN_PASSWORD_HASH = None  # Будет инициализирован при валидации

    @classmethod
    def validate(cls):
        """Проверка обязательных переменных и инициализация безопасности"""
        required_vars = [
            "TELEGRAM_TOKEN",
            "DATABASE_URL",
            "EMAIL_USER",
            "EMAIL_PASSWORD",
            "ADMIN_EMAIL",
            "WEBHOOK_URL"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        # Проверка ADMIN_ID
        if cls.ADMIN_ID == 0:
            missing.append("ADMIN_ID")
        
        if missing:
            sys.exit(f"Ошибка: Отсутствуют переменные окружения: {', '.join(missing)}")
        
        # Инициализация хеша пароля
        admin_pass = os.getenv("ADMIN_PASSWORD")
        if admin_pass:
            cls.ADMIN_PASSWORD_HASH = bcrypt.hashpw(
                admin_pass.encode(), 
                bcrypt.gensalt()
            ).decode()
        else:
            print("Предупреждение: ADMIN_PASSWORD не установлен")

# Проверка при импорте модуля
Config.validate()