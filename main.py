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
from handlers.start import start_menu
from handlers.categories import handle_categories, show_packages
from handlers.callbacks import get_callback_handlers
from handlers.extra import get_extra_handler
from handlers.instructors import get_instructors_handlers
from handlers.gallery import get_gallery_handlers
from handlers.admin import get_admin_handlers
from handlers.back import get_back_handler
from handlers.profile import handle_profile

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Пост-инициализация для вебхука"""
    await asyncio.sleep(2)
    if Config.ENV == "production":
        await application.bot.set_webhook(
            url=Config.WEBHOOK_URL,
            certificate=open('ssl_cert.pem', 'rb') if Config.ENV == "production" else None
        )
        logger.info("Webhook установлен: %s", Config.WEBHOOK_URL)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error("Ошибка: %s", context.error, exc_info=True)
    if update.effective_message:
        await update.effective_message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

def register_handlers(application):
    """Регистрация всех обработчиков"""
    # Основные команды
    application.add_handler(CommandHandler("start", start_menu))

    # Категории и пакеты
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))

    # Обратные звонки и доп. занятия
    for handler in get_callback_handlers():
        application.add_handler(handler)
    application.add_handler(get_extra_handler())

    # Инструкторы и галерея
    for handler in get_instructors_handlers():
        application.add_handler(handler)
    for handler in get_gallery_handlers():
        application.add_handler(handler)

    # Админ-панель
    for handler in get_admin_handlers():
        application.add_handler(handler)

    # Личный кабинет
    application.add_handler(CallbackQueryHandler(handle_profile, pattern="^profile$"))

    # Навигация "Назад"
    application.add_handler(get_back_handler())

    # Обработка ошибок
    application.add_error_handler(error_handler)

def main():
    """Точка входа"""
    try:
        logger.info("Запуск бота...")
        
        application = Application.builder() \
            .token(Config.TELEGRAM_TOKEN) \
            .post_init(post_init) \
            .build()

        register_handlers(application)

        # Режим запуска
        if Config.ENV == "production":
            application.run_webhook(
                listen="0.0.0.0",
                port=Config.PORT,
                webhook_url=Config.WEBHOOK_URL,
                key="private.key",
                cert="cert.pem"
            )
        else:
            application.run_polling()

    except Exception as e:
        logger.critical("Критическая ошибка: %s", str(e))
        raise

if __name__ == "__main__":
    main()