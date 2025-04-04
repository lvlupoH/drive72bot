# handlers/personal.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_personal_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик личного кабинета с кнопкой назад"""
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    
    await update.message.reply_text(
        "Добро пожаловать в личный кабинет!\n\n"
        "Здесь вы можете:\n"
        "- Просматривать расписание\n"
        "- Проверять баланс\n"
        "- Смотреть прогресс обучения",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def personal_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик возврата из личного кабинета"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Возвращаемся в главное меню...")
    # Логика возврата реализуется через back_handler