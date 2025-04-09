import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,  # Добавлен импорт
    ContextTypes,
    filters  # Добавлен импорт
)
from config import Config
from handlers import categories, callbacks, admin, gallery, instructors

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def post_init(application):
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(categories.handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(categories.show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(gallery.show_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(instructors.show_instructors, pattern="^instructors$"))
    application.add_handler(callbacks.setup_callbacks_handler())
    
    # Защита от неизвестных команд
    application.add_handler(MessageHandler(
        filters.COMMAND & ~filters.Regex(r'^/(start|admin|cancel)$'),
        lambda update, ctx: update.message.reply_text("⚠️ Неизвестная команда!")
    ))
    
    # Админ-панель
    for handler in admin.get_admin_handler():
        application.add_handler(handler)
    
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()