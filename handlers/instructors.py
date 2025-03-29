from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

async def show_instructors(update, context):
    """Показ карточек инструкторов"""
    instructors = [
        {
            'name': 'Иван Петров',
            'category': 'A, A1',
            'phone': '+7 900 123-45-67',
            'telegram_id': '@ivan_petrov'
        },
        {
            'name': 'Мария Сидорова',
            'category': 'B',
            'phone': '+7 900 765-43-21', 
            'telegram_id': '@maria_sid'
        }
    ]
    
    for instructor in instructors:
        text = (
            f"🏍️ Инструктор: {instructor['name']}\n"
            f"📌 Категория: {instructor['category']}\n"
            f"📱 Телефон: {instructor['phone']}\n"
            f"📩 Telegram: {instructor['telegram_id']}"
        )
        
        keyboard = [
            [InlineKeyboardButton("Написать", url=f"tg://user?id={instructor['telegram_id']}")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        
        await update.callback_query.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
