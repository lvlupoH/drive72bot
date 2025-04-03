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

ADMIN_PASSWORD = "Drive"
(
    AWAIT_PASSWORD,
    GET_TG_ID,
    GET_FULLNAME,
    GET_GROUP,
    GET_EXAMS,
    CONFIRM,
    DELETE_STUDENT
) = range(7)

# ----- Регистрация студента -----
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль админа:")
    return AWAIT_PASSWORD

async def auth_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    await update.message.reply_text("Введите Telegram ID студента:")
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
    return CONFIRM

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_text("✅ Студент зарегистрирован!")
    return ConversationHandler.END

# ----- Удаление студента -----
async def delete_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
    
    await update.message.reply_text("Введите Telegram ID студента для удаления:")
    return DELETE_STUDENT

async def delete_student_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.message.text
    context.user_data["delete_tg_id"] = tg_id
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=tg_id).first()
        if not student:
            await update.message.reply_text("❌ Студент не найден!")
            return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="delete_confirm")],
        [InlineKeyboardButton("❌ Отмена", callback_data="delete_cancel")]
    ]
    await update.message.reply_text(
        f"Удалить студента с ID: {tg_id}?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

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
                await query.edit_message_text("🗑️ Студент удален!")
            else:
                await query.edit_message_text("⚠️ Студент уже удален")
    else:
        await query.edit_message_text("❌ Удаление отменено")
    
    context.user_data.clear()
    return ConversationHandler.END

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin_start),
            CommandHandler("delete", delete_student_start)
        ],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            GET_TG_ID: [MessageHandler(filters.TEXT, get_tg_id)],
            GET_FULLNAME: [MessageHandler(filters.TEXT, get_fullname)],
            GET_GROUP: [MessageHandler(filters.TEXT, get_group)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm_data)],
            DELETE_STUDENT: [MessageHandler(filters.TEXT, delete_student_confirm)]
        },
        fallbacks=[
            CallbackQueryHandler(delete_student_final, pattern="^delete_")
        ],
        allow_reentry=True
    )