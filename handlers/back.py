from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    
    if data[1] == "main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Доп. занятия", callback_data="extra_classes")],
            [InlineKeyboardButton("Адреса", callback_data="contacts")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text("🏠 Главное меню:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data[1] == "categories":
        keyboard = [
            [InlineKeyboardButton("Категория А", callback_data="cat_a")],
            [InlineKeyboardButton("Категория В", callback_data="cat_b")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
        ]
        await query.edit_message_text("🏍 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    context.user_data.clear()