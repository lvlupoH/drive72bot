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
BACK_BUTTON = InlineKeyboardButton("🔙 Назад", callback_data="back")

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
        [BACK_BUTTON]
    ]
    await send_message(update, "Админ-панель:", keyboard)
    context.user_data["prev_state"] = ADMIN_MENU
    return ADMIN_MENU

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prev_state = context.user_data.get("prev_state")
    if prev_state == ADMIN_MENU:
        return await show_admin_menu(update, context)
    elif prev_state == SELECT_GROUP:
        return await list_students(update, context)
    # Добавьте другие состояния по аналогии
    return ConversationHandler.END

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        groups = session.query(Student.group).distinct().all()
    
    buttons = [
        [InlineKeyboardButton(f"Группа {group[0]}", callback_data=f"group_{group[0]}")]
        for group in groups
    ]
    buttons.append([BACK_BUTTON])
    await send_message(update, "Выберите группу:", buttons)
    context.user_data["prev_state"] = SELECT_GROUP
    return SELECT_GROUP

# ... (остальные функции аналогично, с обработкой кнопки "Назад")

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            ADMIN_MENU: [
                CallbackQueryHandler(list_students, pattern="^list_students"),
                CallbackQueryHandler(add_student_flow, pattern="^add_student"),
                CallbackQueryHandler(delete_student_flow, pattern="^delete_student"),
                CallbackQueryHandler(back_handler, pattern="^back")
            ],
            # ... остальные состояния
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
        allow_reentry=True
    )