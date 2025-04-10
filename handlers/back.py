from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')[1]
    
    if data == "main":
        keyboard = [
            [{"text": "Категории", "callback_data": "categories"}],
            [{"text": "Обратный звонок", "callback_data": "callback_request"}],
            [{"text": "Дополнительные занятия", "callback_data": "extra_classes"}],
            [{"text": "Адреса и контакты", "callback_data": "contacts"}],
            [{"text": "Галерея", "callback_data": "gallery"}],
            [{"text": "Личный кабинет", "callback_data": "profile"}]
        ]
        await query.edit_message_text(
            "Главное меню:",
            reply_markup={"inline_keyboard": keyboard}
        )
    
    elif data == "categories":
        keyboard = [
            [InlineKeyboardButton("Категория А, А1", callback_data="cat_a")],
            [InlineKeyboardButton("Категория В", callback_data="cat_b")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "Выберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )