from telegram import Update
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        # Логика возврата в главное меню
        pass
    elif query.data == "back_categories":
        # Логика возврата к категориям
        pass
    # Добавьте другие условия по необходимости