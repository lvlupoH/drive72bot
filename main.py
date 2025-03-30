import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import Config
from handlers import (
    categories,
    callbacks,
    gallery,
    instructors,
    admin,
    profile
)

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Инициализация после запуска"""
    await asyncio.sleep(2)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error("Ошибка: %s", context.error, exc_info=True)

def main():
    config = Config()
    
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin.admin_panel))
    
    # Категории
    application.add_handler(CallbackQueryHandler(
        categories.show_categories, 
        pattern="^categories$"
    ))
    
    # Обратный звонок
    application.add_handler(CallbackQueryHandler(
        callbacks.start_callback_request,
        pattern="^callback_request$"
    ))
    
    # Галерея
    application.add_handler(CallbackQueryHandler(
        gallery.show_gallery,
        pattern="^gallery$"
    ))
    
    # Инструкторы
    application.add_handler(CallbackQueryHandler(
        instructors.show_instructors,
        pattern="^instructors$"
    ))
    
    # Личный кабинет
    application.add_handler(CallbackQueryHandler(
        profile.show_profile,
        pattern="^profile$"
    ))
    
    # Ошибки
    application.add_error_handler(error_handler)

    # Запуск
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL,
        secret_token="WEBHOOK_SECRET"
    )

if __name__ == "__main__":
    main()
