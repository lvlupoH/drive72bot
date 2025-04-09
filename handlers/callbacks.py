from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters
)
from config import Config
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging

NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^Обратный звонок$'), start_callback)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False  # Добавлено
    )