from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from config import Config
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

NAME, PHONE, QUESTION = range(3)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Введите ваше имя:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш телефон:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Кратко опишите ваш вопрос:")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    try:
        await send_callback_email(
            context.user_data['name'],
            context.user_data['phone'],
            context.user_data['question']
        )
        await update.message.reply_text("✅ Ваш запрос отправлен администратору!")
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")
        await update.message.reply_text("❌ Ошибка отправки запроса. Попробуйте позже.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запрос отменен")
    return ConversationHandler.END

def get_callback_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

async def send_callback_email(name: str, phone: str, question: str):
    msg = MIMEText(f"Имя: {name}\nТелефон: {phone}\nВопрос: {question}")
    msg['Subject'] = 'Новый запрос обратного звонка'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
            logger.info("Email успешно отправлен")
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")
        raise
