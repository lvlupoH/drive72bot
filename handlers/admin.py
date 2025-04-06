from telegram.ext import CommandHandler, CallbackQueryHandler
from config import Config
import logging

logger = logging.getLogger(__name__)

def get_admin_handler():
    """Возвращает обработчики для админ-панели"""
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_callback, pattern="^admin_")
    ]

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Панель администратора"""
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("Доступ запрещен.")
        return

    keyboard = [
        [{"text": "Статистика", "callback_data": "admin_stats"}],
        [{"text": "Рассылка", "callback_data": "admin_broadcast"}]
    ]
    
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup={"inline_keyboard": keyboard}
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик админских callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_stats":
        await query.edit_message_text("Статистика: 100 пользователей")
    elif query.data == "admin_broadcast":
        await query.edit_message_text("Рассылка в разработке...")
