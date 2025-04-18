from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from models import db  # Исправленный импорт
from utils.config import Config
import hashlib
import re
import logging

logger = logging.getLogger(__name__)

# ... (остальной код обработчиков без изменений)

async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Получаем все группы из БД
    groups = db.get_all_groups()
    
    # Создаем кнопки для каждой группы
    keyboard = [
        [InlineKeyboardButton(f"Группа {group}", callback_data=f"group_{group}")]
        for group in groups
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_admin")])
    
    await query.edit_message_text(
        "📋 Список групп:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_students_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.split('_')[1]
    
    # Получаем учеников группы
    students = db.get_students_by_group(group)
    
    # Создаем кнопки для каждого ученика
    keyboard = [
        [InlineKeyboardButton(f"{s[2]} (@{s[1]})", callback_data=f"student_{s[1]}")]
        for s in students
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="students_list")])
    
    await query.edit_message_text(
        f"👥 Ученики группы {group}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_student_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = query.data.split('_')[1]
    
    # Получаем данные ученика
    student = db.get_student(username)
    
    text = f"""
    👤 Детали ученика:
    ФИО: {student[2]}
    Телефон: {student[3]}
    Группа: {student[5]}
    Категория: {student[4]}
    Период обучения: {student[6]}
    Экзамены:
    - Теория (внутр.): {student[7]}
    - Теория (гос.): {student[8]}
    - Практика: {student[9]}
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data=f"group_{student[5]}")]
    ]
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )