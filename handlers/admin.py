from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from config import Config
import psycopg2
import hashlib
import logging

logger = logging.getLogger(__name__)

# Состояния админ-панели
(ADMIN_AUTH,ADD_USERNAME, ADD_FULLNAME, ADD_PHONE,ADD_CATEGORY, ADD_GROUP, ADD_PERIOD,ADD_EXAM_THEORY, ADD_EXAM_GOS, ADD_EXAM_PRACTICE,DELETE_STUDENT) = range(10)

ADMIN_PASSWORD_HASH = hashlib.sha256(b"Drive").hexdigest()

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)

# ------------------- Аутентификация -------------------
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return ConversationHandler.END
    
    await update.message.reply_text("🔑 Введите пароль администратора:")
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

# ------------------- Управление учениками -------------------
async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    await query.edit_message_text("Введите username ученика (@example):")
    return ADD_USERNAME

async def add_student_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введите ФИО ученика:")
    return ADD_FULLNAME

async def add_student_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fullname'] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return ADD_PHONE

async def add_student_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Введите категорию (A/B/C/D):")
    return ADD_CATEGORY

async def add_student_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Введите номер группы:")
    return ADD_GROUP

async def add_student_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    await update.message.reply_text("Введите период обучения (например: 01.09.2023-30.05.2024):")
    return ADD_PERIOD

async def add_student_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['period'] = update.message.text
    await update.message.reply_text("Введите дату внутреннего теоретического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_THEORY

async def add_student_exam_theory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exam_theory'] = update.message.text
    await update.message.reply_text("Введите дату гос. теоретического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_GOS

async def add_student_exam_gos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exam_gos'] = update.message.text
    await update.message.reply_text("Введите дату практического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_PRACTICE

async def add_student_exam_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exam_practice'] = update.message.text
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students 
            (username, fullname, phone, category, group_num, 
            period, exam_theory, exam_gos, exam_practice)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            context.user_data['username'],
            context.user_data['fullname'],
            context.user_data['phone'],
            context.user_data['category'],
            context.user_data['group'],
            context.user_data['period'],
            context.user_data['exam_theory'],
            context.user_data['exam_gos'],
            context.user_data['exam_practice']
        ))
        conn.commit()
        await update.message.reply_text("✅ Ученик успешно добавлен!")
    except Exception as e:
        logger.error(f"Ошибка добавления: {str(e)}")
        await update.message.reply_text("❌ Ошибка при добавлении ученика!")
    finally:
        conn.close()
    
    context.user_data.clear()
    return ConversationHandler.END

# ------------------- Удаление ученика -------------------
async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("Введите username ученика для удаления:")
    return DELETE_STUDENT

async def process_delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE username = %s", (username,))
        conn.commit()
        
        if cur.rowcount == 0:
            await update.message.reply_text("❌ Ученик не найден!")
        else:
            await update.message.reply_text("✅ Ученик успешно удален!")
    except Exception as e:
        logger.error(f"Ошибка удаления: {str(e)}")
        await update.message.reply_text("❌ Ошибка при удалении!")
    finally:
        conn.close()
    
    return ConversationHandler.END

# ------------------- Отмена действий -------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END

def get_admin_handler():
    return [
        ConversationHandler(
            entry_points=[CommandHandler('admin', admin_start)],
            states={
                ADMIN_AUTH: [MessageHandler(filters.TEXT, admin_auth)],
                ADD_USERNAME: [MessageHandler(filters.TEXT, add_student_username)],
                ADD_FULLNAME: [MessageHandler(filters.TEXT, add_student_fullname)],
                ADD_PHONE: [MessageHandler(filters.TEXT, add_student_phone)],
                ADD_CATEGORY: [MessageHandler(filters.TEXT, add_student_category)],
                ADD_GROUP: [MessageHandler(filters.TEXT, add_student_group)],
                ADD_PERIOD: [MessageHandler(filters.TEXT, add_student_period)],
                ADD_EXAM_THEORY: [MessageHandler(filters.TEXT, add_student_exam_theory)],
                ADD_EXAM_GOS: [MessageHandler(filters.TEXT, add_student_exam_gos)],
                ADD_EXAM_PRACTICE: [MessageHandler(filters.TEXT, add_student_exam_practice)],
                DELETE_STUDENT: [MessageHandler(filters.TEXT, process_delete_student)]
            },
            fallbacks=[
                CommandHandler('cancel', cancel),
                CallbackQueryHandler(cancel, pattern="^back_")
            ]
        )
    ]