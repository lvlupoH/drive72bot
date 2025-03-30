from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.categories import handle_categories

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Инструктора", callback_data="instructors")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text(
            text="Главное меню",
            reply_markup=InlineKeyboardMarkup(keyboard)
            
    elif data == "back_categories":
        await handle_categories(update, context)
