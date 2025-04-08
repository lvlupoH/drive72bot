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
ADMIN_AUTH, ADMIN_ACTION, ADD_STUDENT, DELETE_STUDENT = range(4)
# Состояния для добавления ученика
FULL_NAME, USERNAME, PHONE, GROUP, THEORY_INT, THEORY_STATE, PRACTICE = range(7)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен")
        return ConversationHandler.END
    
    await update.message.reply_text("🔑 Введите пароль администратора:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == Config.ADMIN_PASSWORD:
        # Успешная авторизация
        context.user_data["admin_auth"] = True  # Сохраняем статус
        
        # Показываем меню админ-панели
        keyboard = [
            [InlineKeyboardButton("Добавить ученика", callback_data="add_student")],
            [InlineKeyboardButton("Список учеников", callback_data="list_students")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await update.message.reply_text(
            "🔐 Админ-панель:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_ACTION  # Переход в состояние ADMIN_ACTION
        
    else:
        await update.message.reply_text("❌ Неверный пароль")
        return ConversationHandler.END  # Завершаем диалог

async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("admin_auth"):
        await update.message.reply_text("❌ Требуется авторизация")
        return ConversationHandler.END
        
    await update.message.reply_text("Введите ФИО ученика:")
    return FULL_NAME  # Следующее состояние

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("Введите username ученика (@username):")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Введите группу:")
    return GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    await update.message.reply_text("Дата внутреннего экзамена (ГГГГ-ММ-ДД):")
    return THEORY_INT

async def get_theory_int(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['theory_internal'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    await update.message.reply_text("Дата гос. экзамена (ГГГГ-ММ-ДД):")
    return THEORY_STATE

async def get_theory_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['theory_state'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    await update.message.reply_text("Дата практического экзамена (ГГГГ-ММ-ДД):")
    return PRACTICE

async def get_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['practice'] = datetime.strptime(update.message.text, "%Y-%m-%d")
    
    # Сохранение в БД
    db = next(get_db())
    student = Student(**context.user_data)
    db.add(student)
    db.commit()
    
    await update.message.reply_text("✅ Ученик успешно добавлен!")
    context.user_data.clear()
    return ConversationHandler.END

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    students = db.query(Student).all()
    
    if not students:
        await update.callback_query.message.reply_text("Список учеников пуст")
        return
    
    text = "📚 Список учеников:\n\n"
    for student in students:
        text += (
            f"👤 {student.full_name}\n"
            f"📱 @{student.username}\n"
            f"📅 Группа: {student.group}\n\n"
        )
    
    await update.callback_query.message.reply_text(text)

async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Введите username ученика для удаления:")
    return DELETE_STUDENT

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    db = next(get_db())
    student = db.query(Student).filter(Student.username == username).first()
    
    if student:
        db.delete(student)
        db.commit()
        await update.message.reply_text("✅ Ученик удален")
    else:
        await update.message.reply_text("❌ Ученик не найден")
    
    return ConversationHandler.END

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Возврат в главное меню")
    return ConversationHandler.END

def get_admin_handler():
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_start)],
            states={
                ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)],
                ADMIN_ACTION: [
                    CallbackQueryHandler(list_students, pattern="^list_students$"),
                    CallbackQueryHandler(add_student_start, pattern="^add_student$"),
                    CallbackQueryHandler(delete_student, pattern="^delete_student$"),
                    CallbackQueryHandler(admin_back, pattern="^back_main$")
                ],
                ADD_STUDENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_username),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_group),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_theory_int),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_theory_state),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_practice)
                ]
            },
            fallbacks=[CommandHandler("cancel", admin_back)],
            per_user=True
        )
    ]