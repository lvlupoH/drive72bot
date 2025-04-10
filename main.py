import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from config import Config
from handlers import (
    start,
    categories,
    callbacks,
    extra,
    instructors,
    gallery,
    admin,
    back,
    profile
)
from database import get_db

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Инициализация после запуска"""
    await asyncio.sleep(2)
    await application.bot.set_webhook(
        url=Config.WEBHOOK_URL,
        certificate=open('ssl_cert.pem', 'rb') if Config.ENV == 'production' else None
    )
    logger.info("Webhook установлен")

def setup_handlers(application):
    """Регистрация всех обработчиков"""
    # Основные команды
    application.add_handler(CommandHandler("start", start.handle_start))
    
    # Обработчики категорий
    application.add_handler(CallbackQueryHandler(
        categories.handle_categories, 
        pattern="^categories$"
    ))
    application.add_handler(CallbackQueryHandler(
        categories.show_packages, 
        pattern="^(cat_a|cat_b)$"
    ))
    
    # Обратные звонки и доп. занятия
    application.add_handler(callbacks.get_callback_handler())
    application.add_handler(extra.get_extra_handler())
    
    # Инструкторы и галерея
    application.add_handler(CallbackQueryHandler(
        instructors.instructors_handler, 
        pattern="^instructors$"
    ))
    application.add_handler(CallbackQueryHandler(
        gallery.gallery_handler, 
        pattern="^gallery$"
    ))
    
    # Личный кабинет
    application.add_handler(CallbackQueryHandler(
        profile.handle_profile,
        pattern="^profile$"
    ))
    
    # Админ-панель
    for handler in admin.get_admin_handlers():
        application.add_handler(handler)
    
    # Навигация "Назад"
    application.add_handler(CallbackQueryHandler(
        back.handle_back,
        pattern="^back_"
    ))
    
    # Обработка ошибок
    application.add_error_handler(error_handler)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    
    if update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
        )

def main():
    """Точка входа в приложение"""
    try:
        logger.info("Запуск бота...")
        
        application = Application.builder() \
            .token(Config.TELEGRAM_TOKEN) \
            .post_init(post_init) \
            .build()

        setup_handlers(application)
        
        # Режим работы: Webhook для продакшена, Polling для разработки
        if Config.ENV == "production":
            application.run_webhook(
                listen="0.0.0.0",
                port=Config.PORT,
                key="private.key",
                cert="cert.pem",
                webhook_url=Config.WEBHOOK_URL
            )
        else:
            application.run_polling()
            
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()