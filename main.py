import logging
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import Config
from handlers import (
    start,
    setup_callbacks_handler,
    setup_requests_handler,
    back_handler,
    get_admin_handler,
    profile_handler
)

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(app: Application) -> None:
    """Инициализация вебхука после запуска"""
    await app.bot.set_webhook(Config.WEBHOOK_URL)

def main() -> None:
    # Создание приложения
    application = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_handler, pattern=r"^back_"))
    application.add_handler(setup_callbacks_handler())
    application.add_handler(setup_requests_handler())
    application.add_handler(profile_handler())

    # Админ-панель
    for handler in get_admin_handler():
        application.add_handler(handler)

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    asyncio.run(main())
