# handlers/admin.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import Config
import logging

logger = logging.getLogger(__name__)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("⚠️ Доступ запрещен!")
        return

    keyboard = [
        [{"text": "Статистика", "callback_data": "admin_stats"}],
        [{"text": "Рассылка", "callback_data": "admin_broadcast"}],
        [{"text": "Назад", "callback_data": "back_main"}]
    ]
    
    await update.message.reply_text(
        "⚙️ Админ-панель:",
        reply_markup={"inline_keyboard": keyboard}
    )

def get_admin_handler():
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_panel, pattern="^admin_")
    ]
