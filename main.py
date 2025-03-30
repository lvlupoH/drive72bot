from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
from handlers import (
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back,
    get_callback_conversation_handler,  # Новый импорт
    show_gallery,
    show_instructors,
    admin_panel
)

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_cabinet")]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    config = Config()
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_callback_conversation_handler())  # Добавлен ConversationHandler
    
    # Остальные обработчики...
    
    if config.DEPLOY_ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL)
    else:
        application.run_polling()

if __name__ == "__main__":
    main()
