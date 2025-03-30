from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,  # Добавленный импорт
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from config import Config
import smtplib
from email.mime.text import MIMEText

# Стадии диалога
NAME, PHONE, QUESTION = range(3)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало запроса обратного звонка"""
    await update.callback_query.message.reply_text("Введите ваше имя:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш телефон:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Кратко опишите вопрос:")
    return QUESTION

async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    name = context.user_data['name']
    phone = context.user_data['phone']
    
    msg = MIMEText(f"Имя: {name}\nТелефон: {phone}\nВопрос: {question}")
    msg['Subject'] = 'Новый запрос обратного звонка'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
        await update.message.reply_text("✅ Заявка отправлена!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    return ConversationHandler.END

def get_callback_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PHONE: [MessageHandler(filters.TEXT, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT, send_request)]
        },
        fallbacks=[]
    )
