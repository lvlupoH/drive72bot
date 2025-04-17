from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
import logging
from datetime import datetime
from .back import back_handler
from database import db

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_type = "Обратный звонок" if query.data == "callback_request" else "Дополнительные занятия"
    context.user_data['request_type'] = request_type
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await query.edit_message_text(
        f"📝 {request_type}\n\nВведите ваше ФИО:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_callback")]]
    await update.message.reply_text(
        "📱 Введите ваш номер телефона:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not phone.replace('+', '').isdigit():
        await update.message.reply_text("❌ Некорректный номер телефона!")
        return PHONE
    context.user_data['phone'] = phone
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_callback")]]
    await update.message.reply_text(
        "❓ Введите ваш вопрос:",
        reply_markup=InlineKeyboardMarkup(keyboard))
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
        db.add_request({
            'type': context.user_data['request_type'],
            'name': context.user_data['name'],
            'phone': context.user_data['phone'],
            'question': context.user_data['question'],
            'username': user.username
        })
        await update.message.reply_text("✅ Данные отправлены администратору!")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await update.message.reply_text("❌ Ошибка отправки!")
    
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

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Ошибка SMTP: {str(e)}")
        raise

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^(callback_request|extra_classes)$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[
            CommandHandler('cancel', lambda update, context: ConversationHandler.END),
            CallbackQueryHandler(back_handler, pattern="^back_")
        ],
        per_message=True,  # Исправлено
        allow_reentry=True
    )