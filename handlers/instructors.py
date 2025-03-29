from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config

async def show_instructors(update, context):
    query = update.callback_query
    await query.answer()

    # Клавиатура с кнопкой "Назад"
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]

    # Формируем сообщение с карточками инструкторов
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
    for idx, instructor in enumerate(instructors, 1):
        response += (
            f"{idx}. {instructor['name']}\n"
            f"• Категория: {instructor['category']}\n"
            f"• Телефон: {instructor['phone']}\n"
            f"• Telegram: {instructor['tg_id']}\n\n"
        )

    # Отправляем сообщение с клавиатурой
    await query.edit_message_text(
        text=response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
