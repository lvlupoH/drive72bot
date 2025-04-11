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
from .back import back_handler  # Добавьте этот импорт

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Добавляем кнопку "Назад" сразу в первый шаг
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]]
    
    await query.edit_message_text(
        "📞 Запрос обратного звонка\n\nПожалуйста, введите ваше ФИО:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_callback")]]
    await update.message.reply_text(
        "📱 Теперь введите ваш номер телефона:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_callback")]]
    await update.message.reply_text(
        "❓ Опишите ваш вопрос:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    
    try:
        # Отправка email
        await send_email(
            request_type="Обратный звонок",
            name=context.user_data['name'],
            phone=context.user_data['phone'],
            question=context.user_data['question'],
            username=user.username
        )
        # Запись в БД (пример для PostgreSQL)
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO callback_requests (name, phone, question, username) VALUES (%s, %s, %s, %s)",
            (context.user_data['name'], context.user_data['phone'], context.user_data['question'], user.username)
        )
        conn.commit()
        await update.message.reply_text("✅ Ваш запрос принят!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Произошла ошибка!")
    finally:
        context.user_data.clear()
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

async def send_email(request_type: str, name: str, phone: str, question: str, username: str):
    body = f"""
    <b>Новый запрос:</b> {request_type}
    <b>ФИО:</b> {name}
    <b>Телефон:</b> {phone}
    <b>Вопрос:</b> {question}
    <b>Username:</b> @{username}
    <b>Дата:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
    """
    
    msg = MIMEText(body, 'html')
    msg['Subject'] = f'📞 Запрос от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

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
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(back_handler, pattern="^back_")  # Теперь back_handler доступен
        ],
        allow_reentry=True
    )