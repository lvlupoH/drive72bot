from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

LESSONS = {
    "Контраварийное вождение": "5000₽ за занятие",
    "Парковка": "3000₽ за занятие",
    "Городское вождение": "4000₽ за занятие",
    "Подготовка к экзамену": "4500₽ за занятие"
}

async def handle_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for name, price in LESSONS.items():
        buttons.append([InlineKeyboardButton(
            f"{name} - {price}",
            callback_data=f"lesson_{name}"
        )])
    
    buttons.append([
        InlineKeyboardButton("Записаться", url="https://driveavto72.ru/contacts"),
        InlineKeyboardButton("Назад", callback_data="back_main")
    ])
    
    await query.edit_message_text(
        text="Дополнительные занятия:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )