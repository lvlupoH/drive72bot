from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from config import Config
from handlers.categories import (
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back
)
from handlers.callbacks import start_callback, get_name, get_phone, get_question, cancel
from handlers.gallery import show_gallery
from handlers.instructors import show_instructors
from handlers.admin import admin_panel, setup_admin_handlers
from database import init_db
import logging

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация БД
init_db()

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_cabinet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive! Выберите опцию:",
        reply_markup=reply_markup
    )

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Обработчик категорий
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_moto_packages, pattern="^cat_moto$"))
    application.add_handler(CallbackQueryHandler(show_auto_packages, pattern="^cat_auto$"))
    application.add_handler(CallbackQueryHandler(show_package_details, pattern="^package_"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back_"))

    # Обработчик обратного звонка
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)

    # Другие обработчики
    application.add_handler(CallbackQueryHandler(show_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(show_instructors, pattern="^instructors$"))
    
    # Админ-обработчики
    setup_admin_handlers(application)

    # Запуск бота
    if config.ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            secret_token='WEBHOOK_SECRET'
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    main()
