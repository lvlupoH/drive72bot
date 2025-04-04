# handlers/back.py
from telegram import Update
from telegram.ext import ContextTypes
from .categories import handle_categories
from .utils import show_admin_menu, list_students

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")]
        ]
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "back_categories":
        await handle_categories(update, context)
    elif query.data == "back_admin":
        await show_admin_menu(update, context)
    elif query.data == "back_groups":
        await list_students(update, context)