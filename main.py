import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
from config import Config
from handlers.categories import handle_categories, show_packages
from handlers.callbacks import setup_callbacks_handler
from handlers.admin import get_admin_handler
from handlers.gallery import show_gallery
from handlers.instructors import show_instructors
from handlers.profile import get_profile_handler
from handlers.back import back_handler

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с главным меню"""
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Доп. занятия", "callback_data": "extra_lessons"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    
    await update.message.reply_text(
        "🚗 Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )

async def post_init(application):
    """Пост-инициализация для вебхуков"""
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    """Основная функция инициализации бота"""
    config = Config()
    
    # Создание приложения
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики меню
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(show_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(show_instructors, pattern="^instructors$"))
    
    # Обратный звонок (ConversationHandler)
    application.add_handler(setup_callbacks_handler())
    
    # Админ-панель
    for handler in get_admin_handler():
        application.add_handler(handler)
    
    # Личный кабинет
    for handler in get_profile_handler():
        application.add_handler(handler)
    
    # Навигация "Назад"
    application.add_handler(CallbackQueryHandler(back_handler, pattern=r"^back_"))

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()