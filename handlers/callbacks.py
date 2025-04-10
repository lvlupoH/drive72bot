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

# Общий обработчик для обоих типов запросов
async def start_request(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: str):
    context.user_data['request_type'] = request_type
    await update.message.reply_text(
        f"📝 {request_type}\n\nВведите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_request(update, context, "Обратный звонок")

async def extra_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_request(update, context, "Дополнительные занятия")

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("❓ Введите ваш вопрос:")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    
    try:
        await send_email(
            request_type=context.user_data['request_type'],
            name=context.user_data['name'],
            phone=context.user_data['phone'],
            question=context.user_data['question'],
            username=user.username
        )
        await update.message.reply_text("✅ Данные отправлены администратору!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка отправки!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

async def send_email(request_type: str, name: str, phone: str, question: str, username: str):
    body = f"""
    Тип запроса: {request_type}
    Имя: {name}
    Телефон: {phone}
    Вопрос: {question}
    Username: @{username}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📞 {request_type} от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_start, pattern="^callback_request$"),
            CallbackQueryHandler(extra_start, pattern="^extra_classes$"),
            CallbackQueryHandler(callback_start, pattern="^contacts_callback$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )