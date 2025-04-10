from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from .back import back_handler  # Добавлен импорт
from config import Config
import hashlib
import psycopg2
import logging

logger = logging.getLogger(__name__)

# Состояния админ-панели
ADMIN_AUTH, ADD_USERNAME, ADD_FULLNAME, ADD_PHONE, ADD_CATEGORY, ADD_GROUP, ADD_PERIOD, ADD_EXAM_THEORY, ADD_EXAM_GOS, ADD_EXAM_PRACTICE = range(10)
ADMIN_PASSWORD_HASH = hashlib.sha256(b"Drive").hexdigest()

# Подключение к БД
def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = hashlib.sha256(update.message.text.encode()).hexdigest()
    if user_input != ADMIN_PASSWORD_HASH:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📋 Список учеников", callback_data="students_list")],
        [InlineKeyboardButton("➕ Добавить ученика", callback_data="add_student")],
        [InlineKeyboardButton("🗑️ Удалить ученика", callback_data="delete_student")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    await update.message.reply_text(
        "⚙️ Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['student'] = {}
    await query.edit_message_text("Введите username ученика (@username):")
    return ADD_USERNAME

async def process_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['username'] = update.message.text
    await update.message.reply_text("Введите ФИО ученика:")
    return ADD_FULLNAME

async def process_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['fullname'] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return ADD_PHONE

async def process_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['phone'] = update.message.text
    await update.message.reply_text("Введите категорию (А/B):")
    return ADD_CATEGORY

async def process_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['category'] = update.message.text
    await update.message.reply_text("Введите группу:")
    return ADD_GROUP

async def process_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['group'] = update.message.text
    await update.message.reply_text("Введите период обучения (например: 01.09.2023-01.03.2024):")
    return ADD_PERIOD

async def process_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['period'] = update.message.text
    await update.message.reply_text("Введите дату внутреннего теоретического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_THEORY

async def process_exam_theory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['exam_theory'] = update.message.text
    await update.message.reply_text("Введите дату гос. теоретического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_GOS

async def process_exam_gos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['exam_gos'] = update.message.text
    await update.message.reply_text("Введите дату практического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_PRACTICE

async def process_exam_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['exam_practice'] = update.message.text
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students 
            (username, fullname, phone, category, group_num, period, exam_theory, exam_gos, exam_practice)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            context.user_data['student']['username'],
            context.user_data['student']['fullname'],
            context.user_data['student']['phone'],
            context.user_data['student']['category'],
            context.user_data['student']['group'],
            context.user_data['student']['period'],
            context.user_data['student']['exam_theory'],
            context.user_data['student']['exam_gos'],
            context.user_data['student']['exam_practice']
        ))
        conn.commit()
        await update.message.reply_text("✅ Ученик успешно добавлен!")
    except Exception as e:
        logger.error(f"Ошибка добавления ученика: {e}")
        await update.message.reply_text("❌ Ошибка добавления!")
    finally:
        conn.close()
    
    context.user_data.clear()
    return ConversationHandler.END

def get_admin_handler():
    return [
        ConversationHandler(
            entry_points=[CommandHandler('admin', admin_start)],
            states={
                ADMIN_AUTH: [MessageHandler(filters.TEXT, admin_auth)],
                ADD_USERNAME: [MessageHandler(filters.TEXT, process_username)],
                ADD_FULLNAME: [MessageHandler(filters.TEXT, process_fullname)],
                ADD_PHONE: [MessageHandler(filters.TEXT, process_phone)],
                ADD_CATEGORY: [MessageHandler(filters.TEXT, process_category)],
                ADD_GROUP: [MessageHandler(filters.TEXT, process_group)],
                ADD_PERIOD: [MessageHandler(filters.TEXT, process_period)],
                ADD_EXAM_THEORY: [MessageHandler(filters.TEXT, process_exam_theory)],
                ADD_EXAM_GOS: [MessageHandler(filters.TEXT, process_exam_gos)],
                ADD_EXAM_PRACTICE: [MessageHandler(filters.TEXT, process_exam_practice)]
            },
            fallbacks=[CallbackQueryHandler(back_handler, pattern="^back_")]
        )
    ]
    