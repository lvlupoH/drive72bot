from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

INSTRUCTORS = {
    "Алексей": "Опыт 10 лет, специалист по категории А",
    "Дмитрий": "Опыт 8 лет, специалист по категории В",
    "Елена": "Опыт 5 лет, инструктор по вождению",
    "Михаил": "Опыт 12 лет, мастер спорта по автоспорту"
}

async def handle_instructors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for name, desc in INSTRUCTORS.items():
        buttons.append([InlineKeyboardButton(
            f"{name} - {desc}",
            callback_data=f"instructor_{name}"
        )])
    
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_main")])
    
    await query.edit_message_text(
        text="Наши инструктора:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )