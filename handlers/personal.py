# handlers/personal.py
from telegram import Update
from telegram.ext import ContextTypes

async def handle_personal_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик личного кабинета"""
    await update.message.reply_text("Добро пожаловать в личный кабинет!")
