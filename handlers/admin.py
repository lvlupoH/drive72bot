from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from utils.config import Config
from .back import back_handler  # Добавьте эту строку в начало файла
from models.database import db
import hashlib
import logging
import re

logger = logging.getLogger(__name__)

# Состояния админ-панели
(
    ADMIN_AUTH,
    ADD_USERNAME, 
    ADD_FULLNAME, 
    ADD_PHONE,
    ADD_CATEGORY, 
    ADD_GROUP, 
    ADD_PERIOD,
    ADD_EXAM_THEORY, 
    ADD_EXAM_GOS,
    ADD_EXAM_PRACTICE,
    DELETE_STUDENT,
    SHOW_STUDENTS
) = range(12)

ADMIN_PASSWORD_HASH = hashlib.sha256(b"Drive").hexdigest()
MAX_LOGIN_ATTEMPTS = 3

def validate_phone(phone: str) -> bool:
    return re.match(r'^\+?[1-9]\d{9,14}$', phone) is not None

def validate_date(date: str) -> bool:
    return re.match(r'\d{2}\.\d{2}\.\d{4}', date) is not None

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return ConversationHandler.END
    context.user_data['login_attempts'] = 0
    await update.message.reply_text("🔑 Введите пароль администратора:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['login_attempts'] += 1
    if context.user_data['login_attempts'] > MAX_LOGIN_ATTEMPTS:
        await update.message.reply_text("🚫 Превышено число попыток!")
        return ConversationHandler.END
    
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
    if not validate_phone(update.message.text):
        await update.message.reply_text("❌ Неверный формат телефона! Пример: +79123456789")
        return ADD_PHONE
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Введите категорию (A/B/C/D):")
    return ADD_CATEGORY

async def add_student_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text.upper()
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
    if not validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return ADD_EXAM_THEORY
    context.user_data['exam_theory'] = update.message.text
    await update.message.reply_text("Введите дату гос. теоретического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_GOS

async def add_student_exam_gos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return ADD_EXAM_GOS
    context.user_data['exam_gos'] = update.message.text
    await update.message.reply_text("Введите дату практического экзамена (ДД.ММ.ГГГГ):")
    return ADD_EXAM_PRACTICE

async def add_student_exam_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return ADD_EXAM_PRACTICE
    context.user_data['exam_practice'] = update.message.text
    
    try:
        db.add_student({
            'username': context.user_data['username'],
            'fullname': context.user_data['fullname'],
            'phone': context.user_data['phone'],
            'category': context.user_data['category'],
            'group_num': context.user_data['group'],
            'period': context.user_data['period'],
            'exam_theory': context.user_data['exam_theory'],
            'exam_gos': context.user_data['exam_gos'],
            'exam_practice': context.user_data['exam_practice']
        })
        await update.message.reply_text("✅ Ученик успешно добавлен!")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("❌ Ошибка при добавлении ученика!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def show_students_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        students = db.get_all_students()
        groups = {}
        for student in students:
            group = student[5]
            if group not in groups:
                groups[group] = []
            groups[group].append(student)
        
        buttons = []
        for group in sorted(groups.keys()):
            buttons.append([InlineKeyboardButton(f"Группа {group}", callback_data=f"group_{group}")])
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_admin")])
        
        await query.edit_message_text(
            text="📋 Список групп:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return SHOW_STUDENTS
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await query.edit_message_text("❌ Не удалось загрузить список учеников!")
        return ConversationHandler.END

async def show_group_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.split('_')[1]
    
    try:
        students = db.get_students_by_group(group)
        buttons = []
        for student in students:
            buttons.append([InlineKeyboardButton(
                f"{student[2]} ({student[1]})", 
                callback_data=f"student_{student[0]}"
            )])
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="students_list")])
        
        await query.edit_message_text(
            text=f"👥 Ученики группы {group}:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return SHOW_STUDENTS
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await query.edit_message_text("❌ Не удалось загрузить список учеников!")
        return ConversationHandler.END

async def show_student_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    student_id = query.data.split('_')[1]
    
    try:
        student = db.get_student_by_id(student_id)
        text = f"""
        👤 Ученик:
        ФИО: {student[2]}
        Телефон: {student[3]}
        Категория: {student[4]}
        Группа: {student[5]}
        Период обучения: {student[6]}
        
        📅 Даты экзаменов:
        - Внутренний теория: {student[7]}
        - Гос. теория: {student[8]}
        - Практика: {student[9]}
        """
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=f"group_{student[5]}")]]
        await query.edit_message_text(
            text=text.strip(),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SHOW_STUDENTS
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await query.edit_message_text("❌ Не удалось загрузить данные ученика!")
        return ConversationHandler.END

async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите username ученика для удаления:")
    return DELETE_STUDENT

async def process_delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    try:
        db.delete_student(username)
        await update.message.reply_text("✅ Ученик успешно удален!")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("❌ Ошибка при удалении!")
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
                DELETE_STUDENT: [MessageHandler(filters.TEXT, process_delete_student)],
                SHOW_STUDENTS: [
                    CallbackQueryHandler(show_group_students, pattern="^group_"),
                    CallbackQueryHandler(show_student_details, pattern="^student_")
                ]
            },
            fallbacks=[
                CommandHandler('cancel', lambda update, context: ConversationHandler.END),
                CallbackQueryHandler(back_handler, pattern="^back_")
            ]
        ),
        CallbackQueryHandler(show_students_list, pattern="^students_list$")
    ]