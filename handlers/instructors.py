from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

INSTRUCTORS = [
    {
        "name": "Иван Петров",
        "description": "Опыт: 10 лет\nКатегории: A, B",
        "photo": "instructor1.jpg"
    }
]

async def show_instructors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = [
        [InlineKeyboardButton(instructor["name"], callback_data=f"instructor_{i}")]
        for i, instructor in enumerate(INSTRUCTORS)
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_main")])
    
    await query.edit_message_text(
        text="🏍️ Наши инструкторы:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )