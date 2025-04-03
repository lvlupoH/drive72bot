# main.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from config import Config
from models import Student, Session
import re

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Используйте /admin для входа")
    return ConversationHandler.END

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
    context.user_data["prev_states"] = [ADMIN_MENU]
    return ADMIN_MENU

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prev_states = context.user_data.get("prev_states", [])
    if not prev_states:
        return await show_admin_menu(update, context)
    
    prev_state = prev_states.pop()
    
    if prev_state == ADMIN_MENU:
        return await show_admin_menu(update, context)
    elif prev_state == SELECT_GROUP:
        return await list_students(update, context)
    elif prev_state == SELECT_STUDENT:
        return await show_group_students(update, context)
    elif prev_state == EDIT_FIELD:
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
    context.user_data["prev_states"].append(SELECT_GROUP)
    return SELECT_GROUP

async def show_group_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    group = query.data.split("_")[1] if query else context.user_data.get("current_group")
    context.user_data["current_group"] = group
    
    with Session() as session:
        students = session.query(Student).filter_by(group=group).all()
    
    buttons = [
        [InlineKeyboardButton(f"{s.fullname} (ID: {s.tg_id})", callback_data=f"student_{s.id}")]
        for s in students
    ]
    buttons.append([BACK_BUTTON])
    
    await send_or_edit(update, f"Студенты группы {group}:", buttons)
    context.user_data["prev_states"].append(SELECT_STUDENT)
    return SELECT_STUDENT

async def select_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    student_id = int(query.data.split("_")[1])
    
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
    context.user_data["prev_states"].append(EDIT_FIELD)
    return EDIT_FIELD

async def edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    field = query.data.split("_")[1]
    context.user_data["edit_field"] = field
    await query.message.reply_text(f"Введите новое значение для {get_field_name(field)}:")
    return CONFIRM_EDIT

async def save_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_value = update.message.text
    field = context.user_data["edit_field"]
    student_id = context.user_data["current_student"]
    
    with Session() as session:
        student = session.get(Student, student_id)
        setattr(student, field, new_value)
        session.commit()
    
    await update.message.reply_text("✅ Изменения сохранены!")
    return await select_student(update, context)

async def delete_student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_or_edit(update, "Введите Telegram ID студента для удаления:", [])
    return DELETE_FLOW

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.message.text
    context.user_data["delete_tg_id"] = tg_id
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=tg_id).first()
        if not student:
            await update.message.reply_text("❌ Студент не найден!")
            return await show_admin_menu(update, context)
    
    buttons = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="delete_confirm")],
        [InlineKeyboardButton("❌ Отмена", callback_data="delete_cancel")]
    ]
    await send_or_edit(update, f"Удалить студента с ID {tg_id}?", buttons)
    return ADMIN_MENU

async def delete_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "delete_confirm":
        with Session() as session:
            student = session.query(Student).filter_by(
                tg_id=context.user_data["delete_tg_id"]
            ).first()
            if student:
                session.delete(student)
                session.commit()
                await query.edit_message_text("✅ Студент удален!")
            else:
                await query.edit_message_text("⚠️ Студент не найден")
    else:
        await query.edit_message_text("❌ Удаление отменено")
    return await show_admin_menu(update, context)

# ======================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =======================
async def send_or_edit(update, text, keyboard=None):
    if keyboard is None:
        keyboard = []
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
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

def get_field_name(field):
    names = {
        "fullname": "ФИО",
        "group": "Группу",
        "internal": "Дату внутреннего экзамена",
        "state": "Дату гос. экзамена",
        "practical": "Дату практики",
        "address": "Адрес"
    }
    return names.get(field, "Поле")

# ======================= НАСТРОЙКА ПРИЛОЖЕНИЯ =======================
def main():
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            ADMIN_MENU: [
                CallbackQueryHandler(list_students, pattern="^list_students$"),
                CallbackQueryHandler(delete_student_flow, pattern="^delete_student$"),
                CallbackQueryHandler(delete_final, pattern="^delete_"),
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
                CallbackQueryHandler(edit_field, pattern="^edit_"),
                CallbackQueryHandler(handle_back, pattern="^back$")
            ],
            CONFIRM_EDIT: [MessageHandler(filters.TEXT, save_edit)],
            DELETE_FLOW: [MessageHandler(filters.TEXT, confirm_delete)]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()