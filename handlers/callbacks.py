from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
import smtplib
from email.mime.text import MIMEText
from config import Config

NAME, PHONE, QUESTION = range(3)

async def start_callback_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Введите ваше имя:")
    return NAME

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш телефон:")
    return PHONE

async def send_callback_email(name: str, phone: str):
    msg = MIMEText(f"Новый запрос обратного звонка:\nИмя: {name}\nТелефон: {phone}")
    msg['Subject'] = 'Обратный звонок'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)
