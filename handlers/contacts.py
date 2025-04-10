from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📍 Филиал 1", url="https://2gis.ru/tyumen/geo/70000001019159851")],
        [InlineKeyboardButton("📍 Филиал 2", url="https://2gis.ru/tyumen/geo/1830115629746447")],
        [InlineKeyboardButton("📍 Филиал 3", url="https://2gis.ru/tyumen/geo/70000001044540338")],
        [InlineKeyboardButton("📍 Филиал 4", url="https://2gis.ru/tyumen/geo/1830115629789564")],
        [InlineKeyboardButton("☎️ Заказать звонок", callback_data="contacts_callback")],
        [InlineKeyboardButton("🌐 Сайт", url="https://driveavto72.ru")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🏢 Наши филиалы:\n",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )