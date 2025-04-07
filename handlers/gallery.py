from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("VK", url="https://vk.com/drive_72"),
            InlineKeyboardButton("Telegram", url="https://t.me/drive_in_soul")
        ],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🔗 Наши соцсети:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )