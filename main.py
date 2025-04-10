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
from handlers import (
    categories,
    callbacks,
    back,
    admin,
    gallery,
    contacts
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Дополнительные занятия", "callback_data": "extra_classes"}],
        [{"text": "Адреса и контакты", "callback_data": "contacts"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "🏎️ Добро пожаловать в Drive72!",
        reply_markup={"inline_keyboard": keyboard}
    )

async def post_init(application):
    await asyncio.sleep(5)
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Регистрация всех обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(back.back_handler, pattern="^back_"))
    app.add_handler(CallbackQueryHandler(categories.handle_categories, pattern="^categories$"))
    app.add_handler(CallbackQueryHandler(categories.show_packages, pattern="^(cat_a|cat_b)$"))
    app.add_handler(CallbackQueryHandler(gallery.handle_gallery, pattern="^gallery$"))
    app.add_handler(CallbackQueryHandler(contacts.handle_contacts, pattern="^contacts$"))
    app.add_handler(callbacks.setup_callbacks_handler())
    app.add_handlers(admin.get_admin_handler())
    
    app.run_polling()
    
    app.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
