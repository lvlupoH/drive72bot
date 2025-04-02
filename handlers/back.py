from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.categories import handle_categories

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Главное меню
    if callback_data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text(
            "🏠 Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Назад к категориям
    elif callback_data == "back_categories":
        await handle_categories(update, context)
    
    # Назад из личного кабинета
    elif callback_data == "back_profile":
        keyboard = [
            [InlineKeyboardButton("Мои экзамены", callback_data="my_exams")],
            [InlineKeyboardButton("История оплат", callback_data="payment_history")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "👤 Личный кабинет:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Регистрация обработчика в main.py
def setup_back_handler():
    return CallbackQueryHandler(back_handler, pattern="^back_")