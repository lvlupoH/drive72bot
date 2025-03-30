import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from config import Config
from handlers import (
    categories,
    callbacks,
    gallery,
    instructors,
    profile,
    admin
)

# main.py
from handlers.callbacks import get_callback_handler  # Явный импорт
from handlers import get_admin_handler  # Добавьте в импорты

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с главным меню"""
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструкторы", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    await update.message.reply_text(
        "🚗 Добро пожаловать в автошколу Drive!\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_init(application: Application):
    """Пост-инициализация для вебхука"""
    await asyncio.sleep(2)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(msg="Ошибка в обработчике:", exc_info=context.error)

def main():
    config = Config()
    for handler in get_admin_handler():
        application.add_handler(handler)
    # Создание приложения
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    application.add_handler(get_callback_handler())  # Регистрация ConversationHandler

    # ================== Регистрация обработчиков ================== #

    # 1. Команда /start
    application.add_handler(CommandHandler("start", start))

    # 2. Обработка категорий
    application.add_handler(CallbackQueryHandler(
        categories.handle_categories,
        pattern="^categories$"
    ))
    application.add_handler(CallbackQueryHandler(
        categories.show_packages,
        pattern="^(cat_a|cat_b)$"
    ))

    # 3. Обратный звонок (ConversationHandler)
    application.add_handler(callbacks.get_callback_handler())

    # 4. Галерея
    application.add_handler(CallbackQueryHandler(
        gallery.show_gallery,
        pattern="^gallery$"
    ))

    # 5. Инструкторы
    application.add_handler(CallbackQueryHandler(
        instructors.show_instructors,
        pattern="^instructors$"
    ))

    # 6. Личный кабинет
    application.add_handler(CallbackQueryHandler(
        profile.show_profile,
        pattern="^profile$"
    ))

    # 7. Админ-панель
    application.add_handler(CommandHandler("admin", admin.admin_panel))
    application.add_handler(CallbackQueryHandler(
        admin.handle_admin_actions,
        pattern="^admin_.+"
    ))

    # 8. Кнопка "Назад"
    application.add_handler(CallbackQueryHandler(
        categories.handle_back,
        pattern="^back_"
    ))

    # 9. Обработка ошибок
    application.add_error_handler(error_handler)

    # ================== Запуск приложения ================== #
    if config.ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            secret_token="WEBHOOK_SECRET"
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    main()
