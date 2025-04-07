from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Фото автошколы", callback_data="gallery_school")],
        [InlineKeyboardButton("Фото с занятий", callback_data="gallery_lessons")],
        [InlineKeyboardButton("Наши выпускники", callback_data="gallery_graduates")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="Галерея автошколы Drive:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )