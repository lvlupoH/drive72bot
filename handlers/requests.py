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

# Состояния для запросов
EXTRA_NAME, EXTRA_PHONE = range(2)
RETAKE_NAME, RETAKE_PHONE = range(2,4)
logger = logging.getLogger(__name__)

async def start_extra_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "📚 Введите ваше ФИО для записи:",
        reply_markup=ReplyKeyboardRemove()
    )
    return EXTRA_NAME

async def get_extra_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra_name'] = update.message.text
    await update.message.reply_text("📱 Введите номер телефона:")
    return EXTRA_PHONE

async def get_extra_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    await send_request_email("Доп. занятия", context.user_data['extra_name'], phone)
    await update.message.reply_text("✅ Заявка принята!")
    context.user_data.clear()
    return ConversationHandler.END

async def start_retake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "🔄 Введите ФИО для пересдачи:",
        reply_markup=ReplyKeyboardRemove()
    )
    return RETAKE_NAME

async def get_retake_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retake_name'] = update.message.text
    await update.message.reply_text("📱 Введите номер телефона:")
    return RETAKE_PHONE

async def get_retake_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    await send_request_email("Пересдача", context.user_data['retake_name'], phone)
    await update.message.reply_text("✅ Заявка принята!")
    context.user_data.clear()
    return ConversationHandler.END

async def send_request_email(request_type: str, name: str, phone: str):
    body = f"""
    Тип запроса: {request_type}
    ФИО: {name}
    Телефон: {phone}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📨 {request_type} - {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_requests_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_extra_lessons, pattern="^extra_lessons$"),
            CallbackQueryHandler(start_retake, pattern="^retake_exam$")
        ],
        states={
            EXTRA_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra_name)],
            EXTRA_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra_phone)],
            RETAKE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_retake_name)],
            RETAKE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_retake_phone)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        per_message=True,
        allow_reentry=True
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END
