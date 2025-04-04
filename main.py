import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import Config
from handlers import (
    admin,
    back,
    callbacks,
    categories,
    profile,
    requests
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======================= ОСНОВНЫЕ КОМАНДЫ =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    has_profile = await profile.check_profile(user_id)
    
    buttons = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Дополнительные занятия", callback_data="extra_lessons")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Наши инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")]
    ]
    
    if has_profile:
        buttons.append([InlineKeyboardButton("Личный кабинет", callback_data="profile")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "🚗 Добро пожаловать в автошколу Drive!",
        reply_markup=reply_markup
    )

# ======================= НАСТРОЙКА ВЕБХУКА =======================

async def post_init(application):
    await application.bot.set_webhook(Config.WEBHOOK_URL)

# ======================= ЗАПУСК ПРИЛОЖЕНИЯ =======================

def main():
    application = Application.builder()\
        .token(Config.TELEGRAM_TOKEN)\
        .post_init(post_init)\
        .build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(callbacks.setup_callbacks_handler())
    application.add_handler(admin.admin_conversation_handler())
    application.add_handler(requests.setup_requests_handler())
    application.add_handler(profile.profile_handler())
    
    # Обработчики категорий
    application.add_handler(CallbackQueryHandler(
        categories.handle_categories, 
        pattern="^categories$"
    ))
    application.add_handler(CallbackQueryHandler(
        categories.show_packages, 
        pattern="^(cat_a|cat_b)$"
    ))
    
    # Навигация назад
    application.add_handler(CallbackQueryHandler(
        back.back_handler, 
        pattern=r"^back_(main|categories|admin|groups|requests|profile)$"
    ))
    
    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()