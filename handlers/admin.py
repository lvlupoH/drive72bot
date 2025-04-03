from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from config import Config
from models import Student, Session
import re

# Состояния диалога
(
    AWAIT_PASSWORD,
    ADMIN_MENU,
    ADD_STUDENT,
    GET_TG_ID,
    GET_FULLNAME,
    GET_GROUP,
    GET_EXAMS,
    SELECT_GROUP,
    SELECT_STUDENT,
    EDIT_FIELD,
    CONFIRM_EDIT,
    DELETE_FLOW
) = range(12)

ADMIN_PASSWORD = "Drive"
BACK_BUTTON = InlineKeyboardButton("🔙 Назад", callback_data="back")

# ======================= ОСНОВНЫЕ ХЕНДЛЕРЫ =======================
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль админа:")
    return AWAIT_PASSWORD

async def auth_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    return await show_admin_menu(update, context)

# ======================= НАВИГАЦИЯ =======================
async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Список студентов", callback_data="list_students")],
        [InlineKeyboardButton("➕ Добавить студента", callback_data="add_student")],
        [InlineKeyboardButton("🗑️ Удалить студента", callback_data="delete_student")],
        [BACK_BUTTON]
    ]
    await send_or_edit(update, "Админ-панель:", keyboard)
    return ADMIN_MENU

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current_state = context.user_data.get('prev_states', []).pop()
    
    if current_state == ADMIN_MENU:
        return await show_admin_menu(update, context)
    elif current_state == SELECT_GROUP:
        return await list_students(update, context)
    elif current_state == SELECT_STUDENT:
        return await show_group_students(update, context)
    elif current_state == EDIT_FIELD:
        return await select_student(update, context)
    
    return ConversationHandler.END

# ======================= РАБОТА СО СТУДЕНТАМИ =======================
async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        groups = session.query(Student.group).distinct().all()
    
    buttons = [
        [InlineKeyboardButton(f"Группа {group[0]}", callback_data=f"group_{group[0]}")]
        for group in groups
    ]
    buttons.append([BACK_BUTTON])
    
    await send_or_edit(update, "Выберите группу:", buttons)
    context.user_data.setdefault('prev_states', []).append(ADMIN_MENU)
    return SELECT_GROUP

async def show_group_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    group = query.data.split("_")[1] if query else context.user_data["current_group"]
    context.user_data["current_group"] = group
    
    with Session() as session:
        students = session.query(Student).filter_by(group=group).all()
    
    buttons = [
        [InlineKeyboardButton(f"{s.fullname} (ID: {s.tg_id})", callback_data=f"student_{s.id}")]
        for s in students
    ]
    buttons.append([BACK_BUTTON])
    
    await send_or_edit(update, f"Студенты группы {group}:", buttons)
    context.user_data.setdefault('prev_states', []).append(SELECT_GROUP)
    return SELECT_STUDENT

async def select_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_id = int(update.callback_query.data.split("_")[1])
    
    with Session() as session:
        student = session.get(Student, student_id)
        context.user_data["current_student"] = student.id
    
    buttons = [
        [InlineKeyboardButton("✏️ ФИО", callback_data="edit_fullname")],
        [InlineKeyboardButton("✏️ Группа", callback_data="edit_group")],
        [InlineKeyboardButton("✏️ Внутренний экзамен", callback_data="edit_internal")],
        [InlineKeyboardButton("✏️ Гос. экзамен", callback_data="edit_state")],
        [InlineKeyboardButton("✏️ Практика", callback_data="edit_practical")],
        [InlineKeyboardButton("✏️ Адрес", callback_data="edit_address")],
        [BACK_BUTTON]
    ]
    
    await send_or_edit(update, get_student_info(student), buttons)
    context.user_data.setdefault('prev_states', []).append(SELECT_STUDENT)
    return EDIT_FIELD

# ======================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =======================
async def send_or_edit(update, text, keyboard):
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def get_student_info(student):
    return (
        f"📝 Редактирование студента:\n\n"
        f"ФИО: {student.fullname}\n"
        f"Группа: {student.group}\n"
        f"Внутренний экзамен: {student.internal_exam}\n"
        f"Гос. экзамен: {student.state_exam}\n"
        f"Практика: {student.practical_exam}\n"
        f"Адрес: {student.address}"
    )

# ======================= НАСТРОЙКА ОБРАБОТЧИКА =======================
def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            ADMIN_MENU: [
                CallbackQueryHandler(list_students, pattern="^list_students$"),
                CallbackQueryHandler(add_student_flow, pattern="^add_student$"),
                CallbackQueryHandler(delete_student_flow, pattern="^delete_student$"),
                CallbackQueryHandler(handle_back, pattern="^back$")
            ],
            SELECT_GROUP: [
                CallbackQueryHandler(show_group_students, pattern="^group_"),
                CallbackQueryHandler(handle_back, pattern="^back$")
            ],
            SELECT_STUDENT: [
                CallbackQueryHandler(select_student, pattern="^student_"),
                CallbackQueryHandler(handle_back, pattern="^back$")
            ],
            EDIT_FIELD: [
                CallbackQueryHandler(select_field_to_edit, pattern="^edit_"),
                CallbackQueryHandler(handle_back, pattern="^back$")
            ],
            CONFIRM_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit)],
            DELETE_FLOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
        allow_reentry=True,
        per_message=True
    )
