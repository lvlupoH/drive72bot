import os
from telegram import Update
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
    categories,
    callbacks,
    gallery,
    instructors,
    admin
)

async def post_init(application):
    """Установка вебхука после инициализации"""
    await application.bot.set_webhook(
        url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Инструктора", "callback_data": "instructors"}]
    ]
    
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )

def main():
    config = Config()
    
    # Создание приложения с вебхуком
    application = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(categories.handle_categories, pattern="^categories"))
    application.add_handler(callbacks.setup_callbacks_handler())
    application.add_handler(MessageHandler(filters.PHOTO, gallery.handle_photo))
    application.add_handler(CommandHandler("admin", admin.admin_panel))

    # Запуск в зависимости от среды
    if os.environ.get('ENV') == 'production':
        application.run_webhook(
            listen="0.0.0.0",
            port=int(config.PORT),
            webhook_url=config.WEBHOOK_URL,
            secret_token='WEBHOOK_SECRET'
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    main()
