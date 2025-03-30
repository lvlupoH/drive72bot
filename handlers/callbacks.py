# handlers/callbacks.py
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

# Состояния диалога
NAME, PHONE, QUESTION = range(3)

# Настройка логгера
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога обратного звонка"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "📞 Для запроса обратного звонка потребуется:\n\n"
        "1. Ваше имя\n2. Контактный телефон\n3. Краткое описание вопроса\n\n"
        "Пожалуйста, введите ваше имя:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем имя и запрашиваем телефон"""
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    logger.info(f"Имя пользователя {user.first_name}: {update.message.text}")
    
    await update.message.reply_text(
        "📱 Теперь введите ваш номер телефона в формате +7XXX XXX XX XX:",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем телефон и запрашиваем вопрос"""
    user = update.message.from_user
    context.user_data['phone'] = update.message.text
    logger.info(f"Телефон пользователя {user.first_name}: {update.message.text}")
    
    await update.message.reply_text(
        "📝 Кратко опишите ваш вопрос или проблему:",
        reply_markup=ReplyKeyboardRemove()
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация запроса и отправка email"""
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    logger.info(f"Вопрос от {user.first_name}: {update.message.text}")

    try:
        await send_callback_email(
            context.user_data['name'],
            context.user_data['phone'],
            context.user_data['question']
        )
        await update.message.reply_text(
            "✅ Ваш запрос успешно отправлен!\nМы свяжемся с вами в течение 15 минут.",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Ошибка отправки email: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке запроса. Пожалуйста, попробуйте позже."
        )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} отменил запрос")
    
    await update.message.reply_text(
        "❌ Запрос отменен",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def send_callback_email(name: str, phone: str, question: str):
    """Отправка email через SMTP"""
    body = f"""
    <b>Новый запрос обратного звонка</b>
    
    🧑‍💻 Клиент: {name}
    📱 Телефон: {phone}
    ❓ Вопрос: {question}
    
    ⏰ Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    msg = MIMEText(body.strip(), "html")
    msg['Subject'] = f'🚨 Запрос звонка от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_callbacks_handler() -> ConversationHandler:
    """Настройка обработчика диалога"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^callback_request$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex(r'^❌ Отмена$'), cancel)
        ],
        allow_reentry=True
    )
