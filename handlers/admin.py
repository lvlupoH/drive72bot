from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,  # Импорт добавлен
    CallbackQueryHandler,
    ContextTypes
)
from config import Config

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель"""
    if update.effective_user.id not in Config.ADMINS:
        return
    
    keyboard = [
        [InlineKeyboardButton("Добавить расписание", callback_data="add_schedule")],
        [InlineKeyboardButton("Изменить статус пользователя", callback_data="edit_user")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик действий админа"""
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "add_schedule":
        await query.message.reply_text("Введите дату занятия в формате ДД.ММ.ГГГГ:")
    elif action == "edit_user":
        await query.message.reply_text("Введите ID пользователя:")

def get_admin_handler():
    """Возвращает обработчики админ-панели"""
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(handle_admin_actions, pattern="^(add_schedule|edit_user)$")
    ]
