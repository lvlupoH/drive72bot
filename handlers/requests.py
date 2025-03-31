# handlers/requests.py
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

# Состояния для всех запросов
REQUEST_TYPE, NAME, PHONE = range(3)

logger = logging.getLogger(__name__)

async def start_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Определяем тип запроса
    request_type = "Дополнительные занятия" if query.data == "extra_lessons" else "Пересдача"
    context.user_data['request_type'] = request_type
    
    await query.message.reply_text(
        f"📝 Запрос на {request_type}\n\nПожалуйста, введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Теперь введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    request_type = context.user_data['request_type']
    
    try:
        await send_request_email(
            request_type,
            context.user_data['name'],
            context.user_data['phone']
        )
        await update.message.reply_text("✅ Заявка принята! С вами свяжутся для уточнения деталей.")
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

def setup_requests_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_request, pattern="^(extra_lessons|retake_exam)$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        allow_reentry=True
    )
