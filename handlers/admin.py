from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,  # Импорт добавлен
    CommandHandler
)
from config import Config
import logging

logger = logging.getLogger(__name__)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик админ-панели"""
    query = update.callback_query
    user = update.effective_user
    
    # Проверка прав администратора
    if user.id != Config.ADMIN_ID:
        await query.answer("⛔ Доступ запрещен!")
        return
    
    keyboard = [
        [InlineKeyboardButton("Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("Выход", callback_data="admin_exit")]
    ]
    
    await query.edit_message_text(
        text="⚙️ Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик действий админ-панели"""
    query = update.callback_query
    action = query.data.split("_")[1]  # admin_stats → "stats"
    
    if action == "stats":
        # Логика получения статистики
        await query.answer("📊 Статистика: 1000 пользователей")
    
    elif action == "broadcast":
        # Логика рассылки
        await query.answer("📢 Режим рассылки")
    
    elif action == "exit":
        await query.edit_message_text("✅ Сеанс администрирования завершен")

def get_admin_handler():
    """Возвращает обработчики для админ-панели"""
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
        CallbackQueryHandler(handle_admin_actions, pattern=r"^admin_")
    ]