from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from config import Config
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging
import re

# Состояния для разных запросов
CALLBACK_NAME, CALLBACK_PHONE = range(2)
EXTRA_NAME, EXTRA_PHONE = range(2,4)
RETAKE_NAME, RETAKE_PHONE = range(4,6)

logger = logging.getLogger(__name__)
PHONE_REGEX = re.compile(r'^(\+7|8)\d{10}$')

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📞 Запрос обратного звонка\nПожалуйста, введите ваше ФИО:",
            reply_markup=ReplyKeyboardRemove()
        )
        return CALLBACK_NAME
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return ConversationHandler.END

async def get_callback_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['callback_name'] = update.message.text
    await update.message.reply_text("Теперь введите ваш номер телефона в формате 8XXXXXXXXXX:")
    return CALLBACK_PHONE

async def get_callback_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not PHONE_REGEX.match(phone):
        await update.message.reply_text("❌ Неверный формат номера. Попробуйте еще раз:")
        return CALLBACK_PHONE
    
    try:
        await send_request_email(
            "Обратный звонок",
            context.user_data['callback_name'],
            phone
        )
        await update.message.reply_text("✅ Ваш запрос принят! Мы свяжемся с вами в течение 15 минут.")
    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        await update.message.reply_text("❌ Ошибка отправки. Попробуйте позже.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def start_extra_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "📚 Запрос на дополнительные занятия\nВведите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return EXTRA_NAME

async def get_extra_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not PHONE_REGEX.match(phone):
        await update.message.reply_text("❌ Неверный формат номера. Попробуйте еще раз:")
        return EXTRA_PHONE
    
    try:
        await send_request_email(
            "Дополнительные занятия",
            context.user_data['extra_name'],
            phone
        )
        await update.message.reply_text("✅ Заявка принята! Администратор свяжется для уточнения деталей.")
    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        await update.message.reply_text("❌ Ошибка отправки. Попробуйте позже.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def start_retake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "🔄 Запрос на пересдачу экзамена\nВведите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return RETAKE_NAME

async def get_retake_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not PHONE_REGEX.match(phone):
        await update.message.reply_text("❌ Неверный формат номера. Попробуйте еще раз:")
        return RETAKE_PHONE
    
    try:
        await send_request_email(
            "Пересдача экзамена",
            context.user_data['retake_name'],
            phone
        )
        await update.message.reply_text("✅ Заявка принята! Мы согласуем дату пересдачи.")
    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        await update.message.reply_text("❌ Ошибка отправки. Попробуйте позже.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def send_request_email(request_type: str, name: str, phone: str):
    body = f"""Новый запрос: {request_type}
    ФИО: {name}
    Телефон: {phone}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
    
    msg = MIMEText(body)
    msg['Subject'] = f'📨 {request_type} - {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_requests_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^callback_request$"),
            CallbackQueryHandler(start_extra_lessons, pattern="^extra_lessons$"),
            CallbackQueryHandler(start_retake, pattern="^retake_exam$")
        ],
        states={
            CALLBACK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_callback_name)],
            CALLBACK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_callback_phone)],
            EXTRA_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra_name)],
            EXTRA_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra_phone)],
            RETAKE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_retake_name)],
            RETAKE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_retake_phone)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        allow_reentry=True
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END