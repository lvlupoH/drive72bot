from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler  # Добавлено
)
from config import Config
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime  # Добавлено

NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "📞 Запрос обратного звонка\n\nПожалуйста, введите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

... (остальные функции обработчики без изменений)

def setup_callbacks_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^callback_request$")  # Исправлено
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        allow_reentry=True
    )
