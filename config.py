import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config:
    """Конфигурация приложения с валидацией переменных окружения"""
    
    # Основные настройки бота
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не установлен в переменных окружения")
    
    # Настройки базы данных
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не установлен в переменных окружения")
    
    # Email настройки
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "heartilyforward@gmail.com")
    
    # Админские настройки
    ADMIN_ID = int(os.getenv("ADMIN_ID", 249423404))
    ADMINS = [ADMIN_ID]  # Можно добавить несколько админов через запятую в .env
    
    # Webhook настройки
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))  # Порт по умолчанию для вебхуков
    
    # Определение среды выполнения
    ENV = os.getenv("ENV", "production").lower()
    
    @property
    def GALLERY_PATH(self):
        return os.path.abspath(os.getenv("GALLERY_PATH", "gallery"))
    
    # Валидация email настроек
    if not all([EMAIL_USER, EMAIL_PASSWORD]):
        raise RuntimeError("Email credentials не настроены")

    @classmethod
    def check_env(cls):
        """Проверка обязательных переменных окружения"""
        required = [
            'TELEGRAM_TOKEN',
            'DATABASE_URL',
            'EMAIL_USER',
            'EMAIL_PASSWORD'
        ]
        for var in required:
            if not os.getenv(var):
                raise EnvironmentError(f"Необходимо установить {var} в .env")
            
    PAYMENT_URL = os.getenv("PAYMENT_URL", "https://driveavto72.ru/")
    
# Проверка настроек при импорте
Config.check_env()
