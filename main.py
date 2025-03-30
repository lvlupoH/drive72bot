import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    CallbackContext
)

# Загрузка конфигурации
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot_debug.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))

async def post_init(application: Application):
    """Действия после инициализации"""
    try:
        await application.bot.set_webhook(Config.WEBHOOK_URL)
        logger.info("✅ Вебхук установлен на %s", Config.WEBHOOK_URL)
    except Exception as e:
        logger.critical("❌ Ошибка установки вебхука: %s", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    try:
        user = update.effective_user
        logger.info("➡️ /start от %s (%s)", user.full_name, user.id)
        
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")]
        ]
        
        await update.message.reply_text(
            "Добро пожаловать в Drive!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error("⚠️ Ошибка в /start: %s", e)
        await update.message.reply_text("🚫 Произошла ошибка. Попробуйте позже.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error("🔴 Глобальная ошибка: %s", context.error, exc_info=True)
    
    # Отправка сообщения пользователю
    if update:
        await update.effective_message.reply_text(
            "😞 Произошла непредвиденная ошибка. Разработчики уже уведомлены."
        )
    
    # Уведомление админа (пример)
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"🚨 Ошибка в боте:\n{context.error}"
        )

def main():
    """Запуск приложения"""
    try:
        config = Config()
        application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_error_handler(error_handler)
        
        # Логирование конфигурации
        logger.info("⚙️ Конфигурация:\nWEBHOOK: %s\nPORT: %s", 
                  config.WEBHOOK_URL, config.PORT)
        
        # Запуск
        if "render" in config.WEBHOOK_URL:
            application.run_webhook(
                listen="0.0.0.0",
                port=config.PORT,
                webhook_url=config.WEBHOOK_URL,
                allowed_updates=Update.ALL_TYPES
            )
            logger.info("🌐 Режим вебхука активирован")
        else:
            application.run_polling()
            logger.info("🔁 Режим polling активирован")
            
    except Exception as e:
        logger.critical("‼️ Критическая ошибка при запуске: %s", e)

if __name__ == "__main__":
    main()
