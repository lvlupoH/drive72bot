import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import Config
from handlers.categories import handle_categories, show_packages
from handlers.callbacks import setup_callbacks_handler
from handlers.gallery import handle_gallery
from handlers.contacts import handle_contacts
from handlers.back import back_handler  # Добавлен импорт
from handlers.admin import get_admin_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Дополнительные занятия", callback_data="extra_classes")],
        [InlineKeyboardButton("Адреса и контакты", callback_data="contacts")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    await update.message.reply_text(
        "🏎️ Добро пожаловать в Drive72!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_init(application):
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(handle_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(handle_contacts, pattern="^contacts$"))
    application.add_handler(setup_callbacks_handler())
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))  # Исправлено
    application.add_handlers(get_admin_handler())
    
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()