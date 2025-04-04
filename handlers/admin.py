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

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Список студентов", callback_data="list_students")],
        [InlineKeyboardButton("➕ Добавить студента", callback_data="add_student")],
        [InlineKeyboardButton("🗑️ Удалить студента", callback_data="delete_student")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_main")]
    ]
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    return ADMIN_MENU

# ======================= РАБОТА СО СТУДЕНТАМИ =======================

# ---------- Добавление студента ----------
async def add_student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "Введите Telegram ID студента:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]])
    )
    return GET_TG_ID

async def get_tg_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tg_id"] = update.message.text
    await update.message.reply_text(
        "Введите ФИО студента:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]])
    )
    return GET_FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text(
        "Введите номер группы:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]])
    )
    return GET_GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group"] = update.message.text
    await update.message.reply_text(
        "Введите данные в формате:\n"
        "Внутренний экзамен: ДД.ММ.ГГГГ\n"
        "Гос. экзамен: ДД.ММ.ГГГГ\n"
        "Практика: ДД.ММ.ГГГГ\n"
        "Адрес: ул. Примерная, 1",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_admin")]])
    )
    return GET_EXAMS

async def process_exam_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
    address_match = re.search(r"Адрес:\s*(.+)", text)
    
    if len(dates) != 3 or not address_match:
        await update.message.reply_text("❌ Неверный формат данных!")
        return await show_admin_menu(update, context)
    
    with Session() as session:
        student = Student(
            tg_id=context.user_data["tg_id"],
            fullname=context.user_data["fullname"],
            group=context.user_data["group"],
            internal_exam=dates[0],
            state_exam=dates[1],
            practical_exam=dates[2],
            address=address_match.group(1).strip()
        )
        session.add(student)
        session.commit()
    
    await update.message.reply_text("✅ Студент успешно добавлен!")
    return await show_admin_menu(update, context)

# ---------- Список студентов ----------
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
    return SELECT_GROUP

async def show_group_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    group = query.data.split("_")[1]
    context.user_data["current_group"] = group
    
    with Session() as session:
        students = session.query(Student).filter_by(group=group).all()
    
    buttons = [
        [InlineKeyboardButton(
            f"{student.fullname} (ID: {student.tg_id})", 
            callback_data=f"student_{student.id}"
        )] for student in students
    ]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_groups")])
    
    await query.edit_message_text(
        f"Студенты группы {group}:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return SELECT_STUDENT

# ---------- Редактирование студента ----------
async def select_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    student_id = int(query.data.split("_")[1])
    
    with Session() as session:
        student = session.get(Student, student_id)
        context.user_data["edit_student"] = student.id
        context.user_data["student_data"] = {
            "tg_id": student.tg_id,
            "fullname": student.fullname,
            "group": student.group,
            "internal_exam": student.internal_exam,
            "state_exam": student.state_exam,
            "practical_exam": student.practical_exam,
            "address": student.address
        }
    
    keyboard = [
        [InlineKeyboardButton("✏️ ФИО", callback_data="edit_fullname")],
        [InlineKeyboardButton("✏️ Группа", callback_data="edit_group")],
        [InlineKeyboardButton("✏️ Внутренний экзамен", callback_data="edit_internal")],
        [InlineKeyboardButton("✏️ Гос. экзамен", callback_data="edit_state")],
        [InlineKeyboardButton("✏️ Практика", callback_data="edit_practical")],
        [InlineKeyboardButton("✏️ Адрес", callback_data="edit_address")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"back_group_{context.user_data['current_group']}")]
    ]
    
    await query.edit_message_text(
        f"📝 Редактирование студента:\n\n"
        f"ФИО: {context.user_data['student_data']['fullname']}\n"
        f"Группа: {context.user_data['student_data']['group']}\n"
        f"Внутренний экзамен: {context.user_data['student_data']['internal_exam']}\n"
        f"Гос. экзамен: {context.user_data['student_data']['state_exam']}\n"
        f"Практика: {context.user_data['student_data']['practical_exam']}\n"
        f"Адрес: {context.user_data['student_data']['address']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EDIT_FIELD

# Остальные функции остаются без изменений...

# ======================= НАСТРОЙКА ОБРАБОТЧИКА =======================

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_admin)],
            ADMIN_MENU: [
                CallbackQueryHandler(list_students, pattern="^list_students$"),
                CallbackQueryHandler(add_student_flow, pattern="^add_student$"),
                CallbackQueryHandler(delete_student_flow, pattern="^delete_student$"),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            GET_TG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tg_id)],
            GET_FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            GET_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            GET_EXAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_exam_data)],
            SELECT_GROUP: [
                CallbackQueryHandler(show_group_students, pattern="^group_"),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            SELECT_STUDENT: [
                CallbackQueryHandler(select_student, pattern="^student_"),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            EDIT_FIELD: [
                CallbackQueryHandler(select_field_to_edit, pattern="^edit_"),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            CONFIRM_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit)],
            DELETE_FLOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
        allow_reentry=True
    )