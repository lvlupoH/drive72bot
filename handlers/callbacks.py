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
import logging
from datetime import datetime
from email.utils import formatdate

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога обратного звонка"""
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "📞 Запрос обратного звонка\n\n"
        "Пожалуйста, введите ваше имя:",
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
    """Финализация запроса и отправка email"""
    context.user_data['question'] = update.message.text
    user_data = context.user_data

    try:
        # Формируем письмо
        message = MIMEText(
            f"Новый запрос обратного звонка:\n\n"
            f"Имя: {user_data['name']}\n"
            f"Телефон: {user_data['phone']}\n"
            f"Вопрос: {user_data['question']}\n\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        message['Subject'] = f'📞 Запрос звонка от {user_data["name"]}'
        message['From'] = Config.EMAIL_USER
        message['To'] = Config.ADMIN_EMAIL
        message['Date'] = formatdate(localtime=True)

        # Отправка через SMTP с SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.sendmail(
                Config.EMAIL_USER, 
                Config.ADMIN_EMAIL, 
                message.as_string()
            )
            logger.info("Письмо успешно отправлено на %s", Config.ADMIN_EMAIL)

        await update.message.reply_text(
            "✅ Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке. Попробуйте позже."
        )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text(
        "❌ Запрос отменен",
        reply_markup=ReplyKeyboardRemove()
    )
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
        allow_reentry=True
    )
