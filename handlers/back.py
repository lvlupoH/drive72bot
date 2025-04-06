from telegram import Update
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        await start(update, context)
    elif query.data == "back_categories":
        await handle_categories(update, context)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}]
    ]
    await query.edit_message_text(
        "Главное меню:",
        reply_markup={"inline_keyboard": keyboard}
    )
