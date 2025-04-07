from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Мои курсы", callback_data="my_courses")],
        [InlineKeyboardButton("Мои платежи", callback_data="my_payments")],
        [InlineKeyboardButton("Мои данные", callback_data="my_data")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="Личный кабинет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )