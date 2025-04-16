import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import Config
from handlers import (
    handle_categories,
    show_packages,
    show_package_details,
    setup_callbacks_handler,
    get_admin_handler,
    handle_contacts,
    handle_gallery,
    show_profile
)
from database import db
from handlers.back import back_handler  # Добавьте этот импорт

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

async def post_init(app):
    await app.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    db.create_tables()
    
    app = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    app.add_handlers([
        CommandHandler("start", start),
        CallbackQueryHandler(handle_categories, pattern="^categories$"),
        CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"),
        CallbackQueryHandler(show_package_details, pattern="^package_"),
        setup_callbacks_handler(),
        CallbackQueryHandler(handle_gallery, pattern="^gallery$"),
        CallbackQueryHandler(handle_contacts, pattern="^contacts$"),
        CallbackQueryHandler(show_profile, pattern="^profile$"),
        *get_admin_handler()
    ])
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()