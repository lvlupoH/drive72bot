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

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога обратного звонка"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📞 Запрос обратного звонка\n\n"
        "Пожалуйста, введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем имя и запрашиваем телефон"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "Теперь введите ваш номер телефона в формате +7XXX XXX XX XX:",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем телефон и запрашиваем вопрос"""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Кратко опишите ваш вопрос или проблему:",
        reply_markup=ReplyKeyboardRemove()
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация запроса"""
    context.user_data['question'] = update.message.text
    
    try:
        await send_callback_email(
            context.user_data['name'],
            context.user_data['phone'],
            context.user_data['question']
        )
        await update.message.reply_text("✅ Ваш запрос успешно отправлен!")
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка при отправке")

    context.user_data.clear()
    return ConversationHandler.END

async def send_callback_email(name: str, phone: str, question: str):
    """Отправка email через SMTP"""
    body = f"""
    Новый запрос обратного звонка:
    
    ФИО: {name}
    Телефон: {phone}
    Вопрос: {question}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📞 Запрос звонка от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

def setup_callbacks_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^Отмена$'), cancel)
        ],
        per_message=False,
        allow_reentry=True
    )