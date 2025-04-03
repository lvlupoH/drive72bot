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
    admin,
    back,
    callbacks,
    categories,
    profile
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    has_profile = await profile.check_profile(user_id)
    
    buttons = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Дополнительные занятия", "callback_data": "extra_classes"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Наши инструктора", "callback_data": "instructors"}],
        [{"text": "Галерея", "callback_data": "gallery"}]
    ]
    
    if has_profile:
        buttons.append([{"text": "Личный кабинет", "callback_data": "profile"}])
    
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": buttons}
    )

async def post_init(application):
    await application.bot.set_webhook(Config.WEBHOOK_URL)

def main():
    application = Application.builder()\
        .token(Config.TELEGRAM_TOKEN)\
        .post_init(post_init)\
        .build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(callbacks.setup_callbacks_handler())
    application.add_handler(admin.admin_conversation_handler())
    application.add_handler(profile.profile_handler())
    application.add_handler(CallbackQueryHandler(categories.handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(categories.show_packages, pattern="^(cat_a|cat_b)$"))
    application.add_handler(CallbackQueryHandler(back.back_handler, pattern="^back_"))
    
    application.run_webhook(
        listen="0.0.0.0",
        port=Config.PORT,
        webhook_url=Config.WEBHOOK_URL,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()