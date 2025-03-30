# handlers/callbacks.py
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

# Состояния диалога
NAME, PHONE, QUESTION = range(3)

# Настройка логгера
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога обратного звонка"""
    await update.message.reply_text(
        "📞 Запрос обратного звонка\n\n"
        "Пожалуйста, введите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем имя и запрашиваем телефон"""
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    logger.info("Имя пользователя %s: %s", user.first_name, update.message.text)
    
    await update.message.reply_text(
        "Теперь введите ваш номер телефона в формате +7XXX XXX XX XX:",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем телефон и запрашиваем вопрос"""
    user = update.message.from_user
    context.user_data['phone'] = update.message.text
    logger.info("Телефон пользователя %s: %s", user.first_name, update.message.text)
    
    await update.message.reply_text(
        "Кратко опишите ваш вопрос или проблему:",
        reply_markup=ReplyKeyboardRemove()
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация запроса и отправка email"""
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    logger.info("Вопрос от %s: %s", user.first_name, update.message.text)

    try:
        # Отправляем email
        await send_callback_email(
            context.user_data['name'],
            context.user_data['phone'],
            context.user_data['question']
        )
        await update.message.reply_text(
            "✅ Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error("Ошибка отправки email: %s", str(e))
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке запроса. Пожалуйста, попробуйте позже."
        )

    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    user = update.message.from_user
    logger.info("Пользователь %s отменил запрос", user.first_name)
    
    await update.message.reply_text(
        "❌ Запрос отменен",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def send_callback_email(name: str, phone: str, question: str):
    """Отправка email через SMTP"""
    # Формируем сообщение
    body = f"""
    Новый запрос обратного звонка:
    
    Имя: {name}
    Телефон: {phone}
    Вопрос: {question}
    
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📞 Запрос звонка от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    # Отправка через SMTP SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_callbacks_handler() -> ConversationHandler:
    """Настройка обработчика диалога"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'^Обратный звонок$'), start_callback)
        ],
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
