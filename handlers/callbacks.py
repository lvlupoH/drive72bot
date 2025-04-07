from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,  # Добавлено
    filters
)
from config import Config
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging

NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

# Обработчик для inline-кнопки
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
    try:
        body = f"""
        Новый запрос звонка:
        Имя: {context.user_data['name']}
        Телефон: {context.user_data['phone']}
        Вопрос: {context.user_data['question']}
        """
        msg = MIMEText(body.strip())
        msg['Subject'] = 'Запрос звонка'
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.ADMIN_EMAIL
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 10000) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        
        await update.message.reply_text("✅ Запрос отправлен!")
    except Exception as e:
        
        logger.info("Письмо отправлено!")
    except Exception as e:
        logger.error(f"Ошибка SMTP: {str(e)}")
        await update.message.reply_text("❌ Ошибка отправки. Попробуйте позже.")
        
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено")
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
        fallbacks=[CommandHandler('cancel', cancel)]
    )