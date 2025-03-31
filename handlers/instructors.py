# handlers/instructors.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

INSTRUCTORS = {
    "ivanov": {
        "name": "Иванов Алексей",
        "bio": "Опыт работы: 10 лет\nКатегории: A, B\nАвто: Volkswagen Golf",
        "phone": "+79123456789",
        "telegram": "https://t.me/ivanov_drive",
        "whatsapp": "https://wa.me/79123456789"
    },
    "petrova": {
        "name": "Петрова Мария", 
        "bio": "Опыт работы: 7 лет\nКатегории: A1, B\nАвто: Hyundai Solaris",
        "phone": "+79876543210",
        "telegram": "https://t.me/petrova_drive",
        "whatsapp": "https://wa.me/79876543210"
    }
}

async def show_instructors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Иванов Алексей", callback_data="instructor_ivanov")],
        [InlineKeyboardButton("Петрова Мария", callback_data="instructor_petrova")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🏫 Наши инструкторы:\nВыберите инструктора:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_instructor_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    instructor_id = query.data.split("_")[1]
    instructor = INSTRUCTORS[instructor_id]
    
    text = (
        f"👤 <b>{instructor['name']}</b>\n\n"
        f"📝 О себе:\n{instructor['bio']}\n\n"
        f"📱 Контакты:\n{instructor['phone']}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📲 Telegram", url=instructor['telegram']),
            InlineKeyboardButton("💬 WhatsApp", url=instructor['whatsapp'])
        ],
        [InlineKeyboardButton("◀️ Назад", callback_data="instructors")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )