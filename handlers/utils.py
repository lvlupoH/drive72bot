# handlers/utils.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import Student, Session

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Список студентов", callback_data="list_students")],
        [InlineKeyboardButton("➕ Добавить студента", callback_data="add_student")],
        [InlineKeyboardButton("🗑️ Удалить студента", callback_data="delete_student")]
    ]
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    with Session() as session:
        groups = session.query(Student.group).distinct().all()
    
    buttons = [
        [InlineKeyboardButton(f"Группа {group[0]}", callback_data=f"group_{group[0]}")]
        for group in groups
    ]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_admin")])
    
    await query.edit_message_text(
        "Выберите группу:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )