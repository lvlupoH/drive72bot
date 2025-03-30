from telegram import Update
from telegram.ext import ContextTypes
from .categories import handle_categories  # Добавлен импорт

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        keyboard = [
            [{"text": "Категории", "callback_data": "categories"}],
            [{"text": "Обратный звонок", "callback_data": "callback_request"}]
        ]
        await query.edit_message_text(
            "Главное меню:",
            reply_markup={"inline_keyboard": keyboard}
        )
    elif query.data == "back_categories":
        await handle_categories(update, context)
