from telegram import Update
from telegram.ext import ContextTypes

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [{"text": "Категории", "callback_data": "categories"}],
        [{"text": "Обратный звонок", "callback_data": "callback_request"}],
        [{"text": "Дополнительные занятия", "callback_data": "extra_lessons"}],
        [{"text": "Инструктора", "callback_data": "instructors"}],
        [{"text": "Галерея", "callback_data": "gallery"}],
        [{"text": "Личный кабинет", "callback_data": "profile"}]
    ]
    await update.message.reply_text(
        "Добро пожаловать в автошколу Drive!",
        reply_markup={"inline_keyboard": keyboard}
    )