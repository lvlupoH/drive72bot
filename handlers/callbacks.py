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

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

# --- Обработчики шагов ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога"""
    await update.message.reply_text(
        "📞 Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем имя и запрашиваем телефон"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем телефон и запрашиваем вопрос"""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("❓ Введите ваш вопрос:")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация и отправка email"""
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    
    try:
        # Отправка email
        await send_callback_email(
            name=context.user_data['name'],
            phone=context.user_data['phone'],
            question=context.user_data['question'],
            username=user.username
        )
        await update.message.reply_text("✅ Данные отправлены администратору!")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await update.message.reply_text("❌ Ошибка отправки!")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text("🚫 Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

# --- Вспомогательные функции ---
async def send_callback_email(name: str, phone: str, question: str, username: str):
    """Отправка email через SMTP"""
    body = f"""
    Новый запрос:
    Имя: {name}
    Телефон: {phone}
    Вопрос: {question}
    Username: @{username}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📞 Запрос от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

# --- Настройка обработчика ---
async def start_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏫 Дополнительные занятия\n\nВведите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'^Обратный звонок$'), start_callback),
            MessageHandler(filters.Regex(r'^Дополнительные занятия$'), start_extra)
        ],
    )