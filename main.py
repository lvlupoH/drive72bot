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
from handlers.back import back_handler
from handlers.callbacks import setup_callbacks_handler
from handlers.admin import get_admin_handler

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [{"text": "🏍 Категории", "callback_data": "categories"}],
        [{"text": "📞 Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "📷 Галерея", "callback_data": "gallery"}],
        [{"text": "👤 Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "🚗 Добро пожаловать в автошколу Drive!\n\n"
        "Выберите нужный раздел:",
        reply_markup={"inline_keyboard": keyboard}
    )

async def post_init(application):
    """Пост-инициализация для вебхука"""
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    """Основная логика приложения"""
    application = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(setup_callbacks_handler())
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))

    # Админ-обработчики
    for handler in get_admin_handler():
        application.add_handler(handler)

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
