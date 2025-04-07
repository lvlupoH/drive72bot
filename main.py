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
from handlers.callbacks import get_callback_handler  # Исправленный импорт
from handlers.admin import get_admin_handler
from handlers.gallery import handle_gallery
from handlers.instructors import handle_instructors
from handlers.profile import handle_profile
from handlers.lessons import handle_lessons

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Дополнительные занятия", "callback_data": "lessons"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )

async def post_init(application):
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_callback_handler())  # Корректное использование
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))
    application.add_handler(CallbackQueryHandler(handle_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(handle_instructors, pattern="^instructors$"))
    application.add_handler(CallbackQueryHandler(handle_profile, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(handle_lessons, pattern="^lessons$"))
    
    # Админ-панель
    for handler in get_admin_handler():
        application.add_handler(handler)
    
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()