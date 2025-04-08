from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from config import Config
from email.mime.text import MIMEText
from datetime import datetime
import aiosmtplib
import logging

logger = logging.getLogger(__name__)
NAME, PHONE, QUESTION = range(3)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📞 Запрос обратного звонка\nПожалуйста, введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Опишите ваш вопрос:")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    try:
        await send_callback_email(
            context.user_data['name'],
            context.user_data['phone'],
            context.user_data['question']
        )
        await update.message.reply_text("✅ Данные отправлены! Ожидайте звонка.")
    
    except aiosmtplib.SMTPAuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {e}")
        
        await update.message.reply_text("❌ Неверный пароль почты.")
    except Exception as e:
        logger.error(f"Другая ошибка: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def send_callback_email(name: str, phone: str, question: str):
    body = f"""
    Новый запрос обратного звонка:
    Имя: {name}
    Телефон: {phone}
    Вопрос: {question}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    message = MIMEText(body.strip())
    message["Subject"] = "📞 Запрос звонка"
    message["From"] = Config.EMAIL_USER
    message["To"] = Config.ADMIN_EMAIL

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=465,
        username=Config.EMAIL_USER,
        password=Config.EMAIL_PASSWORD,
        use_tls=True
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Запрос отменён")
    context.user_data.clear()
    return ConversationHandler.END

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^callback_request$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,  # <-- Добавлено
        per_chat=True,
        per_user=True
    )
    