import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

class Config:
    """Конфигурационный класс для управления настройками приложения"""
    
    # Основные настройки
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Дополнительные параметры
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Уровень логирования
    WEBHOOK_MODE = os.getenv("WEBHOOK_MODE", "False").lower() == "true"  # Режим вебхука
    
    @classmethod
    def validate(cls):
        """Проверка обязательных параметров"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN не найден в .env")
            
        if not cls.ADMIN_ID:
            errors.append("ADMIN_ID не указан")
            
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL отсутствует")

        if errors:
            print("Критические ошибки конфигурации:")
            for error in errors:
                print(f"• {error}")
            sys.exit(1)

# Проверка при импорте модуля
Config.validate()

if __name__ == "__main__":
    # Тест конфигурации
    print("Текущие настройки:")
    print(f"TELEGRAM_TOKEN: {'установлен' if Config.TELEGRAM_TOKEN else 'отсутствует'}")
    print(f"ADMIN_ID: {Config.ADMIN_ID}")
    print(f"DATABASE_URL: {Config.DATABASE_URL[:15]}...")
    print(f"LOG_LEVEL: {Config.LOG_LEVEL}")
    print(f"WEBHOOK_MODE: {Config.WEBHOOK_MODE}")
