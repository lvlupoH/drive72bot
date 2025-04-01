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
from database import get_db
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re
import logging

# Состояния для запросов
(
    EXTRA_NAME, EXTRA_PHONE,
    RETAKE_NAME, RETAKE_PHONE
) = range(4)

logger = logging.getLogger(__name__)
DATE_REGEX = r'\d{2}\.\d{2}\.\d{4}'

# ========== ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ЗАНЯТИЙ ==========
async def start_extra_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога для записи на доп. занятия"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📚 Запись на дополнительные занятия\n\n"
        "Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return EXTRA_NAME

async def get_extra_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra_name'] = update.message.text
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return EXTRA_PHONE

async def get_extra_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra_phone'] = update.message.text
    
    try:
        # Сохранение в базу данных
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO requests (type, full_name, phone)
                    VALUES (%s, %s, %s)
                ''', (
                    'extra_lessons',
                    context.user_data['extra_name'],
                    context.user_data['extra_phone']
                ))
        
        # Отправка email
        await _send_request_email(
            "Дополнительные занятия",
            context.user_data['extra_name'],
            context.user_data['extra_phone']
        )
        
        await update.message.reply_text("✅ Заявка принята! Мы свяжемся с вами для уточнения деталей.")
    
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка при обработке запроса")

    context.user_data.clear()
    return ConversationHandler.END

# ========== ОБРАБОТЧИКИ ПЕРЕСДАЧИ ЭКЗАМЕНА ==========
async def start_retake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога для пересдачи экзамена"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🔄 Запись на пересдачу экзамена\n\n"
        "Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return RETAKE_NAME

async def get_retake_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retake_name'] = update.message.text
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return RETAKE_PHONE

async def get_retake_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retake_phone'] = update.message.text
    
    try:
        # Сохранение в базу данных
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO requests (type, full_name, phone)
                    VALUES (%s, %s, %s)
                ''', (
                    'retake',
                    context.user_data['retake_name'],
                    context.user_data['retake_phone']
                ))
        
        # Отправка email
        await _send_request_email(
            "Пересдача экзамена",
            context.user_data['retake_name'],
            context.user_data['retake_phone']
        )
        
        await update.message.reply_text("✅ Заявка принята! Администратор свяжется с вами.")
    
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка при обработке запроса")

    context.user_data.clear()
    return ConversationHandler.END

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
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        per_message=False,
        conversation_timeout=300
    )
