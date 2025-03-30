from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

def get_admin_handler():
    return [
        CommandHandler("admin", admin_panel)
    ]

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == Config.ADMIN_ID:
        await update.message.reply_text("Админ-панель:")
