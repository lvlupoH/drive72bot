from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

async def show_instructors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    instructors = [
        {
            "name": "Иван Петров",
            "category": "A, A1",
            "phone": "+7 912 345-67-89",
            "tg_id": "@ivan_petrov"
        },
        {
            "name": "Мария Сидорова",
            "category": "B",
            "phone": "+7 987 654-32-10",
            "tg_id": "@maria_sid"
        }
    ]
    
    response = "🏍️ Наши инструкторы:\n\n"
    for instructor in instructors:
        response += (
            f"▪️ {instructor['name']}\n"
            f"Категория: {instructor['category']}\n"
            f"Телефон: {instructor['phone']}\n"
            f"Telegram: {instructor['tg_id']}\n\n"
        )
    
    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_main")]]
    
    # Исправленная строка с закрывающей скобкой
    await query.edit_message_text(
        text=response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
