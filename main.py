import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import Config
from handlers.categories import handle_categories, show_packages, show_package_details
from handlers.callbacks import setup_callbacks_handler
from handlers.admin import get_admin_handler
from handlers.back import back_handler
from handlers.gallery import handle_gallery
from handlers.contacts import handle_contacts
from handlers.profile import show_profile
from database import db

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Доп. занятия", callback_data="extra_classes")],
        [InlineKeyboardButton("Адреса", callback_data="contacts")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    await update.message.reply_text(
        "🏎️ Добро пожаловать в автошколу Drive!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_init(application):
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    config = Config()
    
    # Создание таблиц в базе данных
    db.create_tables()
    
    # Создание приложения
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(show_package_details, pattern="^package_"))
    application.add_handler(setup_callbacks_handler())
    
    # Админ-панель
    admin_handlers = get_admin_handler()
    for handler in admin_handlers:
        application.add_handler(handler)
    
    # Галерея и контакты
    application.add_handler(CallbackQueryHandler(handle_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(handle_contacts, pattern="^contacts$"))
    
    # Личный кабинет
    application.add_handler(CallbackQueryHandler(show_profile, pattern="^profile$"))
    
    # Навигация "Назад"
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))

    # Запуск бота
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()