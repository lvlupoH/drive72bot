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
    show_moto_packages,
    show_auto_packages,
    setup_callbacks_handler,
    show_gallery,
    show_instructors,
    admin_panel
)
import logging

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Инициализация вебхука после запуска"""
    await application.bot.set_webhook(Config.WEBHOOK_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с главным меню"""
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_cabinet")]
    ]
    
    if update.message:
        await update.message.reply_text(
            "🏍️ Добро пожаловать в автошколу Drive!\n"
            "Выберите нужный раздел:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.edit_message_text(
            "🏍️ Добро пожаловать в автошколу Drive!\n"
            "Выберите нужный раздел:",
            reply_markup=InlineKeyboardMarkup(keyboard))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Назад"""
    await start(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирование ошибок"""
    logger.error(msg="Ошибка обработки запроса", exc_info=context.error)

def main():
    """Основная функция инициализации бота"""
    config = Config()
    
    # Создаем приложение
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories"))
    application.add_handler(CallbackQueryHandler(show_moto_packages, pattern="^cat_a"))
    application.add_handler(CallbackQueryHandler(show_auto_packages, pattern="^cat_b"))
    application.add_handler(CallbackQueryHandler(show_gallery, pattern="^gallery"))
    application.add_handler(CallbackQueryHandler(show_instructors, pattern="^instructors"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_main"))
    
    # Диалог обратного звонка
    application.add_handler(setup_callbacks_handler())
    
    # Обработка ошибок
    application.add_error_handler(error_handler)

    # Запуск в зависимости от среды
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
