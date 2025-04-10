from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from config import Config
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime

NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    
    await send_callback_email(
        context.user_data['name'],
        context.user_data['phone'],
        context.user_data['question'],
        user.username
    )
    
    await update.message.reply_text("✅ Данные отправлены!")
    return ConversationHandler.END

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'^(Обратный звонок|Дополнительные занятия)$'), start_callback)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PHONE: [MessageHandler(filters.TEXT, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )