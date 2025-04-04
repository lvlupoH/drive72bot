from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from config import Config
from database import get_db
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging

# Состояния для запросов
(
    EXTRA_NAME, EXTRA_PHONE,
    RETAKE_NAME, RETAKE_PHONE
) = range(4)

logger = logging.getLogger(__name__)

# ========== ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ЗАНЯТИЙ ==========
async def start_extra_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога для записи на доп. занятия"""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await query.message.reply_text(
        "📚 Запись на дополнительные занятия\n\n"
        "Введите ваше ФИО:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return EXTRA_NAME

async def get_extra_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra_name'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await update.message.reply_text(
        "📱 Введите ваш номер телефона:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EXTRA_PHONE

async def get_extra_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra_phone'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await update.message.reply_text(
        "📝 Введите желаемую дату занятий (ДД.ММ.ГГГГ):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END  # Для примера, можно расширить

# ========== ОБРАБОТЧИКИ ПЕРЕСДАЧИ ЭКЗАМЕНА ==========
async def start_retake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога для пересдачи экзамена"""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await query.message.reply_text(
        "🔄 Запись на пересдачу экзамена\n\n"
        "Введите ваше ФИО:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return RETAKE_NAME

async def get_retake_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retake_name'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await update.message.reply_text(
        "📱 Введите ваш номер телефона:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return RETAKE_PHONE

async def get_retake_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retake_phone'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    await update.message.reply_text(
        "📅 Введите дату пересдачи (ДД.ММ.ГГГГ):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END  # Для примера, можно расширить

# ========== ОБЩИЕ ФУНКЦИИ ==========
async def _send_request_email(request_type: str, name: str, phone: str):
    """Отправка email администратору"""
    body = f"""
    Новый запрос: {request_type}
    ФИО: {name}
    Телефон: {phone}
    Время подачи: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📨 Новый запрос: {request_type}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущего диалога"""
    await update.message.reply_text("❌ Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END

def setup_requests_handler():
    """Настройка обработчика диалогов"""
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
            CallbackQueryHandler(cancel, pattern="^back_main$")
        ],
        per_message=False,
        conversation_timeout=300
    )