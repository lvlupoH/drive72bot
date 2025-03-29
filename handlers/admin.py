from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from config import Config

async def admin_panel(update, context):
    if update.effective_user.id not in Config.ADMINS:
        return
    
    keyboard = [
        [InlineKeyboardButton("Добавить расписание", callback_data="add_schedule")],
        [InlineKeyboardButton("Изменить статус пользователя", callback_data="edit_user")]
    ]
    
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def setup_admin_handlers(application):
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^add_schedule|edit_user$"))
