from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler  # Добавлен недостающий импорт
)
from config import Config
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
    return NAME

async def start_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏫 Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("❓ Введите ваш вопрос:")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    request_type = "Обратный звонок" if "callback" in context.user_data else "Доп. занятия"
    
    try:
        # Отправка email
        await send_email(
            request_type=request_type,
            name=context.user_data['name'],
            phone=context.user_data['phone'],
            question=context.user_data['question'],
            username=user.username
        )
        
        # Запись в БД (пример для PostgreSQL)
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests (type, name, phone, question, username)
            VALUES (%s, %s, %s, %s, %s)
        """, (request_type, context.user_data['name'], 
             context.user_data['phone'], context.user_data['question'], user.username))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ Данные отправлены!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка отправки!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

async def send_email(request_type: str, name: str, phone: str, question: str, username: str):
    body = f"""
    Тип запроса: {request_type}
    Имя: {name}
    Телефон: {phone}
    Вопрос: {question}
    Username: @{username}
    Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    """
    
    msg = MIMEText(body.strip())
    msg['Subject'] = f'📞 {request_type} от {name}'
    msg['From'] = Config.EMAIL_USER
    msg['To'] = Config.ADMIN_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        server.send_message(msg)

def setup_callbacks_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_callback, pattern="^callback_request$"),
            CallbackQueryHandler(start_extra, pattern="^extra_classes$"),
            MessageHandler(filters.Regex(r'^☎️ Заказать звонок$'), start_callback)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )