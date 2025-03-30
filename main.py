import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from config import Config
from handlers import categories, callbacks, gallery, instructors, admin

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Стадии для ConversationHandler (обратный звонок)
NAME, PHONE, QUESTION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструкторы", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_cabinet")],
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def post_init(application: Application):
    """Пост-инициализация для установки вебхука"""
    await application.bot.set_webhook(
        url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
    )
    logger.info(f"Вебхук установлен на {Config.WEBHOOK_URL}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(msg="Ошибка в обработчике:", exc_info=context.error)
    
    if update.message:
        await update.message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте позже или свяжитесь с администратором."
        )

def main():
    try:
        # Явная проверка переменных окружения
        Config.validate()
        
        # Создание приложения
        application = Application.builder() \
            .token(Config.TELEGRAM_TOKEN) \
            .post_init(post_init) \
            .build()

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin.admin_panel))
        
        # Обработчики категорий
        application.add_handler(CallbackQueryHandler(
            categories.handle_categories, 
            pattern="^categories$"
        ))
        application.add_handler(CallbackQueryHandler(
            categories.show_moto_packages, 
            pattern="^cat_a$"
        ))
        application.add_handler(CallbackQueryHandler(
            categories.show_auto_packages, 
            pattern="^cat_b$"
        ))

        # Обратный звонок (ConversationHandler)
        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                callbacks.start_callback, 
                pattern="^callback_request$"
            )],
            states={
                NAME: [MessageHandler(filters.TEXT, callbacks.get_name)],
                PHONE: [MessageHandler(filters.TEXT, callbacks.get_phone)],
                QUESTION: [MessageHandler(filters.TEXT, callbacks.get_question)],
            },
            fallbacks=[CommandHandler("cancel", callbacks.cancel)],
        )
        application.add_handler(conv_handler)

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

        # Обработка ошибок
        application.add_error_handler(error_handler)

        # Запуск бота
        if Config.ENV == "production":
            application.run_webhook(
                listen="0.0.0.0",
                port=Config.PORT,
                webhook_url=Config.WEBHOOK_URL,
                secret_token=os.getenv("WEBHOOK_SECRET", None),
            )
        else:
            application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
