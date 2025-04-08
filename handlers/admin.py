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

# Состояния для админ-панели
ADMIN_AUTH, ADMIN_MENU = range(2)
# Состояния для добавления ученика
FULL_NAME, USERNAME, PHONE, CATEGORY, GROUP, THEORY_INT, THEORY_STATE, PRACTICE = range(8)
# Состояния для удаления ученика
DELETE_STUDENT = 8

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен")
        return ConversationHandler.END
    
    await update.message.reply_text("🔑 Введите пароль администратора:")
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
    return ADMIN_MENU

async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await query.edit_message_text(
        "Введите ФИО ученика:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    return FULL_NAME

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Введите username ученика (@username):", reply_markup=InlineKeyboardMarkup(keyboard))
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Введите номер телефона:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Введите категорию (A/B):", reply_markup=InlineKeyboardMarkup(keyboard))
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Введите группу:", reply_markup=InlineKeyboardMarkup(keyboard))
    return GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Дата внутреннего экзамена (ГГГГ-ММ-ДД):", reply_markup=InlineKeyboardMarkup(keyboard))
    return THEORY_INT

async def get_theory_int(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['theory_internal'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Дата гос. экзамена (ГГГГ-ММ-ДД):", reply_markup=InlineKeyboardMarkup(keyboard))
    return THEORY_STATE

async def get_theory_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['theory_state'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await update.message.reply_text("Дата практики (ГГГГ-ММ-ДД):", reply_markup=InlineKeyboardMarkup(keyboard))
    return PRACTICE

async def get_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['practice'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    
    # Сохранение в БД
    db = next(get_db())
    student = Student(**context.user_data)
    db.add(student)
    db.commit()
    
    await update.message.reply_text("✅ Ученик добавлен!")
    context.user_data.clear()
    return await admin_auth(update, context)

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    db = next(get_db())
    students = db.query(Student).order_by(Student.group).all()
    
    if not students:
        await query.message.reply_text("📂 Список учеников пуст")
        return
    
    groups = {}
    for student in students:
        if student.group not in groups:
            groups[student.group] = []
        groups[student.group].append(student)
    
    text = "📚 Список учеников:\n\n"
    for group, students_in_group in groups.items():
        text += f"🏷️ Группа: {group}\n"
        for student in students_in_group:
            text += (
                f"👤 {student.full_name}\n"
                f"📱 @{student.username} | ☎️ {student.phone}\n"
                f"📅 Внутренний экзамен: {student.theory_internal.strftime('%d.%m.%Y')}\n"
                f"🏛️ Гос. экзамен: {student.theory_state.strftime('%d.%m.%Y')}\n"
                f"🚗 Практика: {student.practice.strftime('%d.%m.%Y')}\n\n"
            )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def delete_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]]
    await query.message.reply_text("Введите username или телефон ученика:", reply_markup=InlineKeyboardMarkup(keyboard))
    return DELETE_STUDENT

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identifier = update.message.text
    db = next(get_db())
    
    student = db.query(Student).filter(
        (Student.username == identifier) | 
        (Student.phone == identifier)
    ).first()
    
    if student:
        db.delete(student)
        db.commit()
        await update.message.reply_text("✅ Ученик удален")
    else:
        await update.message.reply_text("❌ Ученик не найден")
    
    return await admin_auth(update, context)

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_admin":
        return await admin_auth(update, context)
    elif query.data == "back_main":
        await query.message.reply_text("Возврат в главное меню")
        return ConversationHandler.END

def get_admin_handler():
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_start)],
            states={
                ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)],
                ADMIN_MENU: [
                    CallbackQueryHandler(add_student_start, pattern="^add_student$"),
                    CallbackQueryHandler(list_students, pattern="^list_students$"),
                    CallbackQueryHandler(delete_student_start, pattern="^delete_student$"),
                    CallbackQueryHandler(back_handler, pattern="^back_")
                ],
                FULL_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                USERNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_username),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                PHONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                CATEGORY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_category),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                GROUP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_group),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                THEORY_INT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_theory_int),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                THEORY_STATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_theory_state),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                PRACTICE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_practice),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ],
                DELETE_STUDENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete),
                    CallbackQueryHandler(back_handler, pattern="^back_admin$")
                ]
            },
            fallbacks=[CommandHandler("cancel", back_handler)],
            per_chat=True,
            per_user=True
        )
    ]