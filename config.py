import os
import sys
from dotenv import load_dotenv
import bcrypt

# Загрузка переменных из .env
load_dotenv()

class Config:
    """Класс конфигурации приложения"""
    
    # Обязательные переменные
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # CDN и дополнительные настройки
    CDN_URL = os.getenv("CDN_URL", "https://default-cdn.com")  # Добавлено значение по умолчанию
    CDN_API_KEY = os.getenv("CDN_API_KEY")
    
    # Безопасность
    ADMIN_PASSWORD_HASH = None

    @classmethod
    def validate(cls):
        """Проверка обязательных переменных"""
        required_vars = [
            "TELEGRAM_TOKEN",
            "DATABASE_URL",
            "ADMIN_ID"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            sys.exit(f"Ошибка: Отсутствуют переменные окружения: {', '.join(missing)}")
        
        # Инициализация пароля администратора
        admin_pass = os.getenv("ADMIN_PASSWORD")
        if admin_pass:
            cls.ADMIN_PASSWORD_HASH = bcrypt.hashpw(
                admin_pass.encode(), 
                bcrypt.gensalt()
            ).decode()
        else:
            print("Предупреждение: ADMIN_PASSWORD не установлен")

# Проверка при импорте
Config.validate()