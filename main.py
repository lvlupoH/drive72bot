import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import Config
from database import init_db
from handlers.categories import handle_categories, show_packages
from handlers.callbacks import setup_callbacks_handler
from handlers.requests import setup_requests_handler
from handlers.admin import get_admin_handler
from handlers.profile import show_profile
from handlers.back import back_handler
from handlers.instructors import show_instructors, show_instructor_details

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Дополнительные занятия", "callback_data": "extra_lessons"}],
        [{"text": "Пересдача", "callback_data": "retake_exam"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "🚗 Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )

async def post_init(application: Application):
    """Пост-инициализация для вебхуков"""
    if Config.ENV == "production":
        await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    init_db()
    
    # Создание приложения
    application = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", show_profile))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))
    application.add_handler(CallbackQueryHandler(show_instructors, pattern="^instructors$"))
    application.add_handler(CallbackQueryHandler(show_instructor_details, pattern="^instructor_"))
    
    # Диалоговые обработчики
    application.add_handler(setup_callbacks_handler())  # Обратный звонок
    application.add_handler(setup_requests_handler())   # Доп. занятия/пересдача
    
    # Админ-панель
    for handler in get_admin_handler():
        application.add_handler(handler)

    # Запуск бота
    if Config.ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=Config.PORT,
            webhook_url=Config.WEBHOOK_URL
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    try:
        logger.info("=== Starting bot ===")
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
