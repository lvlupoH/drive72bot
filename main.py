from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
from handlers import (
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back,
    get_callback_conversation_handler,
    show_gallery,
    show_instructors,
    admin_panel
)
import logging

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
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

async def error_handler(update, context):
    logger.error(msg="Ошибка в обработчике:", exc_info=context.error)

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
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            drop_pending_updates=True  # Важно для избежания конфликтов
        )
    else:
        application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
