from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back,
    get_callback_conversation_handler,
)
import logging

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_cabinet")]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик глобальных ошибок"""
    try:
        if update and update.message:
            await update.message.reply_text("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")
        logger.error("Исключение при обработке обновления:", exc_info=context.error)
    except Exception as e:
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА В ОБРАБОТЧИКЕ ОШИБОК: {e}")

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_callback_conversation_handler())
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_moto_packages, pattern="^cat_moto$"))
    application.add_handler(CallbackQueryHandler(show_auto_packages, pattern="^cat_auto$"))
    application.add_handler(CallbackQueryHandler(show_package_details, pattern="^package_"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back_"))
    application.add_error_handler(error_handler)
    
    # Настройка вебхука
    if config.DEPLOY_ENV == "production":
        logger.info("Запуск в режиме PRODUCTION с вебхуком")
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    else:
        logger.info("Запуск в режиме DEVELOPMENT с поллингом")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    main()
