from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "back_main":
        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Инструктора", callback_data="instructors")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]  # Повторите клавиатуру из /start
        await query.edit_message_text(
            text="Главное меню",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "back_categories":
        # Возврат к выбору категорий
        await handle_categories(update, context)
