import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import Config
from handlers import (
    handle_categories,
    get_callback_handler,
    show_gallery,
    show_instructors,
    show_profile,
    get_admin_handler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_init(app):
    await asyncio.sleep(5)  # Увеличьте задержку до 5 секунд
    await app.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Основные обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_callback_handler())
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(back_main_menu, pattern="^back_main$"))
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^back_categories$"))
    application.add_handler(CallbackQueryHandler(show_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(show_instructors, pattern="^instructors$"))
    application.add_handler(CallbackQueryHandler(show_profile, pattern="^profile$"))
    
    # Админ-обработчики
    for handler in get_admin_handler():
        application.add_handler(handler)
    
    # Запуск
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL,
        secret_token="WEBHOOK_SECRET"
    )

if __name__ == "__main__":
    main()
