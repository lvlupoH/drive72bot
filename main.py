# main.py
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import Config
from handlers import (
    start,
    setup_callbacks_handler,
    setup_requests_handler,
    back_handler,
    get_admin_handler,
    profile_handler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))
    application.add_handler(setup_callbacks_handler())
    application.add_handler(setup_requests_handler())
    application.add_handler(profile_handler())
    
    # Админ-панель
    for handler in get_admin_handler():
        application.add_handler(handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
