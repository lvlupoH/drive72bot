from telegram import Update
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')[1]
    if data == 'main':
        # Вернуться в главное меню
        pass
    elif data == 'categories':
        # Вернуться к категориям
        pass