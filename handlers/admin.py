# handlers/admin.py
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
from .utils import show_admin_menu, list_students
import re

# Состояния диалога
(
    AWAIT_PASSWORD,
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
) = range(11)

ADMIN_PASSWORD = "Drive"

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

# Добавление студента
async def add_student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Введите Telegram ID студента:")
    return GET_TG_ID

async def get_tg_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tg_id"] = update.message.text
    await update.message.reply_text("Введите ФИО студента:")
    return GET_FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text("Введите номер группы:")
    return GET_GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group"] = update.message.text
    await update.message.reply_text(
        "Введите данные в формате:\n"
        "Внутренний экзамен: ДД.ММ.ГГГГ\n"
        "Гос. экзамен: ДД.ММ.ГГГГ\n"
        "Практика: ДД.ММ.ГГГГ\n"
        "Адрес: ул. Примерная, 1"
    )
    return GET_EXAMS

async def process_exam_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
    address_match = re.search(r"Адрес:\s*(.+)", text)
    
    if len(dates) != 3 or not address_match:
        await update.message.reply_text("❌ Неверный формат данных!")
        return ConversationHandler.END
    
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

# Редактирование студента
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
        f"📝 Редактирование студента:\n\n{_format_student_data(context)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EDIT_FIELD

def _format_student_data(context):
    data = context.user_data['student_data']
    return (
        f"ФИО: {data['fullname']}\n"
        f"Группа: {data['group']}\n"
        f"Внутренний экзамен: {data['internal_exam']}\n"
        f"Гос. экзамен: {data['state_exam']}\n"
        f"Практика: {data['practical_exam']}\n"
        f"Адрес: {data['address']}"
    )

async def select_field_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    field = query.data.split("_")[1]
    context.user_data["edit_field"] = field
    
    fields_description = {
        "fullname": "ФИО",
        "group": "Группу",
        "internal": "Дату внутреннего экзамена (ДД.ММ.ГГГГ)",
        "state": "Дату гос. экзамена (ДД.ММ.ГГГГ)",
        "practical": "Дату практики (ДД.ММ.ГГГГ)",
        "address": "Адрес"
    }
    
    await query.message.reply_text(f"✍️ Введите новое значение для {fields_description[field]}:")
    return CONFIRM_EDIT

async def save_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_value = update.message.text
    field = context.user_data["edit_field"]
    student_id = context.user_data["edit_student"]
    
    with Session() as session:
        student = session.get(Student, student_id)
        setattr(student, field, new_value)
        session.commit()
    
    await update.message.reply_text("✅ Изменения успешно сохранены!")
    return await select_student(update, context)

# Удаление студента
async def delete_student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Введите Telegram ID студента:")
    return DELETE_FLOW

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.message.text
    context.user_data["delete_tg_id"] = tg_id
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=tg_id).first()
        if not student:
            await update.message.reply_text("❌ Студент не найден!")
            return await show_admin_menu(update, context)
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="delete_confirm")],
        [InlineKeyboardButton("❌ Отмена", callback_data="delete_cancel")]
    ]
    await update.message.reply_text(
        f"❗️ Удалить студента с ID: {tg_id}?",
        reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU

async def delete_student_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "delete_confirm":
        with Session() as session:
            student = session.query(Student).filter_by(
                tg_id=context.user_data["delete_tg_id"]
            ).first()
            if student:
                session.delete(student)
                session.commit()
                await query.edit_message_text("🗑️ Студент успешно удален!")
            else:
                await query.edit_message_text("⚠️ Студент уже был удален")
    else:
        await query.edit_message_text("❌ Удаление отменено")
    
    context.user_data.clear()
    return await show_admin_menu(update, context)

# Вспомогательные функции
async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Операция отменена")
    context.user_data.clear()
    return ConversationHandler.END

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_admin)],
            ADMIN_MENU: [
                CallbackQueryHandler(list_students, pattern="^list_students$"),
                CallbackQueryHandler(add_student_flow, pattern="^add_student$"),
                CallbackQueryHandler(delete_student_flow, pattern="^delete_student$"),
                CallbackQueryHandler(delete_student_final, pattern="^delete_")
            ],
            GET_TG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tg_id)],
            GET_FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            GET_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            GET_EXAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_exam_data)],
            SELECT_GROUP: [
                CallbackQueryHandler(show_group_students, pattern="^group_"),
                CallbackQueryHandler(show_admin_menu, pattern="^back_groups$")
            ],
            SELECT_STUDENT: [
                CallbackQueryHandler(select_student, pattern="^student_"),
                CallbackQueryHandler(list_students, pattern="^back_group_")
            ],
            EDIT_FIELD: [
                CallbackQueryHandler(select_field_to_edit, pattern="^edit_"),
                CallbackQueryHandler(show_group_students, pattern="^back_group_")
            ],
            CONFIRM_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit)],
            DELETE_FLOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
        allow_reentry=True
    )

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
        reply_markup=InlineKeyboardMarkup(buttons))
    return SELECT_STUDENT