import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_LOGIN = os.getenv("EMAIL_LOGIN")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    VK_LINK = "https://m.vk.com/drive_72?from=search"
    TELEGRAM_CHANNEL_LINK = "https://t.me/drive_in_soul"
