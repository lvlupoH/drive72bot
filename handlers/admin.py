from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
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
    DELETE_STUDENT  # Новое состояние
) = range(7)

# ... остальные функции ...

async def delete_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
    
    await update.message.reply_text("Введите Telegram ID студента для удаления:")
    return DELETE_STUDENT

async def delete_student_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["delete_tg_id"] = update.message.text
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=context.user_data["delete_tg_id"]).first()
        if not student:
            await update.message.reply_text("❌ Студент не найден!")
            return ConversationHandler.END
            
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="confirm_delete")],
        [InlineKeyboardButton("Нет", callback_data="cancel_delete")]
    ]
    
    await update.message.reply_text(
        f"Удалить студента с ID {context.user_data['delete_tg_id']}?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def delete_student_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_delete":
        with Session() as session:
            student = session.query(Student).filter_by(tg_id=context.user_data["delete_tg_id"]).first()
            if student:
                session.delete(student)
                session.commit()
                await query.message.reply_text("✅ Студент успешно удален!")
            else:
                await query.message.reply_text("❌ Студент уже был удален")
    else:
        await query.message.reply_text("❌ Удаление отменено")
    
    context.user_data.clear()
    return ConversationHandler.END

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin_start),
            CommandHandler("delete_student", delete_student_start)  # Новая команда
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
            CallbackQueryHandler(delete_student_final, pattern="^(confirm_delete|cancel_delete)$")
        ]
    )