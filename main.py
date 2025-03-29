import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
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

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация конфигурации
config = Config()

async def post_init(application: Application) -> None:
    """Инициализация вебхука после запуска"""
    await application.bot.set_webhook(config.WEBHOOK_URL)
application = Application.builder() \
    .token(Config.TELEGRAM_TOKEN) \
    .post_init(post_init) \
    .build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Личный кабинет", "callback_data": "personal_cabinet"}],
        [{"text": "Доп. занятия", "callback_data": "extra_lessons"}]
    ]
    
    await update.message.reply_text(
        f"Добро пожаловать в автошколу Drive, {user.first_name}!",
        reply_markup={
            "inline_keyboard": keyboard
        }
    )

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки Назад"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

def setup_handlers(application: Application) -> None:
    """Регистрация всех обработчиков"""
    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin.admin_panel))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(categories.handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(instructors.show_instructors, pattern="^instructors$"))
    application.add_handler(CallbackQueryHandler(gallery.show_gallery, pattern="^gallery$"))
    application.add_handler(CallbackQueryHandler(personal.show_cabinet, pattern="^personal_cabinet$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_main$"))
    
    # Обработчик обратного звонка (ConversationHandler)
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callbacks.start_callback, pattern="^callback_request$")],
        states={
            callbacks.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.get_name)],
            callbacks.PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.get_phone)],
            callbacks.QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.get_question)]
        },
        fallbacks=[CommandHandler("cancel", callbacks.cancel)]
    )
    application.add_handler(conv_handler)
    
    # Обработчик дополнительных занятий
    application.add_handler(CallbackQueryHandler(callbacks.handle_extra_lessons, pattern="^extra_lessons$"))
    
    # Обработчик расписания
    application.add_handler(CallbackQueryHandler(schedule.show_schedule, pattern="^show_schedule$"))
    
    # Админские обработчики
    application.add_handler(CallbackQueryHandler(admin.handle_admin_panel, pattern="^admin_"))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if config.ENV == "development":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Произошла ошибка: {context.error}"
        )

def run_bot() -> None:
    """Запуск бота в нужном режиме"""
    application = Application.builder().token(config.TELEGRAM_TOKEN).post_init(post_init).build()
    
    setup_handlers(application)
    
    if config.ENV == "production":
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=config.WEBHOOK_URL,
            secret_token='WEBHOOK_SECRET'
        )
        logger.info("Бот запущен в режиме WEBHOOK")
    else:
        application.run_polling()
        logger.info("Бот запущен в режиме POLLING")

if __name__ == "__main__":
    run_bot()
