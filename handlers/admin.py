# handlers/admin.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from config import Config

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик админ-панели"""
    if update.effective_user.id not in Config.ADMINS:
        await update.message.reply_text("❌ Доступ запрещен")
        return

    keyboard = [
        [InlineKeyboardButton("Добавить расписание", callback_data="add_schedule")],
        [InlineKeyboardButton("Редактировать пользователей", callback_data="edit_users")],
        [InlineKeyboardButton("Статистика", callback_data="stats")]
    ]
    
    await update.message.reply_text(
        "🛠 Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Добавьте это для правильного импорта
def setup_admin_handlers(application):
    application.add_handler(CommandHandler("admin", admin_panel))
