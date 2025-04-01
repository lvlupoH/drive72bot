import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from config import Config
from handlers import (
    start,
    categories,
    back,
    callbacks,
    requests,
    admin,
    profile,
    instructors
)
from database import init_db

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Инициализация после запуска"""
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    # Инициализация БД
    init_db()
    
    # Создание приложения
    application = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    handlers = [
        CommandHandler("start", start.start),
        CommandHandler("profile", profile.show_profile),
        CallbackQueryHandler(back.back_handler, pattern="^back_"),
        CallbackQueryHandler(categories.handle_categories, pattern="^categories$"),
        CallbackQueryHandler(categories.show_packages, pattern="^(cat_a|cat_b)$"),
        CallbackQueryHandler(instructors.show_instructors, pattern="^instructors$"),
        CallbackQueryHandler(instructors.show_instructor_details, pattern="^instructor_"),
        callbacks.setup_callbacks_handler(),
        requests.setup_requests_handler(),
    ]

    # Добавление админ-панели
    for handler in admin.get_admin_handler():
        handlers.append(handler)

    # Регистрация всех обработчиков
    for handler in handlers:
        application.add_handler(handler)

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    asyncio.run(main())
