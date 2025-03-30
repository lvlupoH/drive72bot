# handlers/profile.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from database import get_user_data  # Предполагается, что функция реализована

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ личного кабинета пользователя"""
    user_id = update.effective_user.id
    
    # Получение данных из БД
    user_data = await get_user_data(user_id)
    
    if not user_data:
        await update.callback_query.answer("❌ Вы не зарегистрированы!")
        return
    
    text = (
        f"👤 Личный кабинет\n\n"
        f"Дата начала обучения: {user_data['start_date']}\n"
        f"Дата окончания: {user_data['end_date']}\n"
        f"Остаток занятий: {user_data['lessons_left']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("Записаться на практику", callback_data="book_practice")],
        [InlineKeyboardButton("Расписание теории", callback_data="theory_schedule")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
