from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from models.student import Student
from models.database import get_db
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
ADMIN_AUTH, ADMIN_MENU, *STEPS = range(10)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен")
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != Config.ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль")
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton("➕ Добавить ученика", callback_data="add_student")],
        [InlineKeyboardButton("📋 Список учеников", callback_data="list_students")],
        [InlineKeyboardButton("🗑️ Удалить ученика", callback_data="delete_student")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    await update.message.reply_text(
        "🔐 Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU

async def add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (логика добавления ученика)
    return ConversationHandler.END

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    students = db.query(Student).all()
    text = "📚 Список учеников:\n\n"
    for student in students:
        text += f"👤 {student.full_name} (@{student.username})\n"
    await update.callback_query.message.reply_text(text)

async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (логика удаления ученика)
    return ConversationHandler.END

def get_admin_handler():
    return [ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)],
            ADMIN_MENU: [
                CallbackQueryHandler(add_student, pattern="^add_student$"),
                CallbackQueryHandler(list_students, pattern="^list_students$"),
                CallbackQueryHandler(delete_student, pattern="^delete_student$"),
                CallbackQueryHandler(back_handler, pattern="^back_main$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True
    )]