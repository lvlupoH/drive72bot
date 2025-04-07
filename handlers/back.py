from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .categories import handle_categories
from .instructors import show_instructors
from .gallery import show_gallery
from .callbacks import start_callback

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data  # Пример: "back_main", "back_categories"
    
    if data == "back_main":
        # Возврат в главное меню
        keyboard = [
            [{"text": "Категории", "callback_data": "categories"}],
            [{"text": "Обратный звонок", "callback_data": "callback_request"}],
            [{"text": "Галерея", "callback_data": "gallery"}],
            [{"text": "Инструктора", "callback_data": "instructors"}],
            [{"text": "Личный кабинет", "callback_data": "profile"}]
        ]
        await query.edit_message_text(
            text="Добро пожаловать в автошколу Drive!",
            reply_markup={"inline_keyboard": keyboard}
        )
    
    elif data == "back_categories":
        # Возврат к списку категорий
        await handle_categories(update, context)
    
    elif data == "back_instructors":
        # Возврат к списку инструкторов
        await show_instructors(update, context)
    
    elif data == "back_gallery":
        # Возврат в галерею
        await show_gallery(update, context)
    
    return