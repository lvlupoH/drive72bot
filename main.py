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
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back,
    get_callback_conversation_handler,
    show_main_menu
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Произошла ошибка: {context.error}")

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_callback_conversation_handler())
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_moto_packages, pattern="^cat_moto$"))
    application.add_handler(CallbackQueryHandler(show_auto_packages, pattern="^cat_auto$"))
    application.add_handler(CallbackQueryHandler(show_package_details, pattern="^package_"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back_"))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Настройка вебхука
    if config.DEPLOY_ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            allowed_updates=Update.ALL_TYPES
        )
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
