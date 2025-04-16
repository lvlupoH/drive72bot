from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📍 рп. Боровский, ул. Набережная д.55, офис 105", url="https://2gis.ru/tyumen/geo/70000001019159851")],
        [InlineKeyboardButton("📍 г. Тюмень, ул. Николая Гондатти д.7/2, офис 210", url="https://2gis.ru/tyumen/geo/1830115629746447")],
        [InlineKeyboardButton("📍 г. Тюмень, ул. Малыгина д.14", url="https://2gis.ru/tyumen/geo/70000001044540338")],
        [InlineKeyboardButton("📍 г. Тюмень, ул. Широтная д.193, корп.1", url="https://2gis.ru/tyumen/geo/1830115629789564")],
        [InlineKeyboardButton("🌐 Сайт Автошколы Drive", url="https://driveavto72.ru")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🏢 Наши филиалы:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    



