from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from config import Config
import logging

logger = logging.getLogger(__name__)
ADMIN_AUTH, ADMIN_ACTION = range(2)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Введите пароль:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == Config.ADMIN_PASSWORD:
        keyboard = [
            [InlineKeyboardButton("Список учеников", callback_data="students_list")],
            [InlineKeyboardButton("Добавить ученика", callback_data="add_student")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await update.message.reply_text(
            "Админ-панель:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_ACTION
    else:
        await update.message.reply_text("❌ Неверный пароль")
        return ConversationHandler.END

async def manage_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Функционал в разработке 🛠️")

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выход из админки")
    return ConversationHandler.END

def get_admin_handler():
    return [ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)],
            ADMIN_ACTION: [CallbackQueryHandler(manage_students)]
        },
        fallbacks=[CommandHandler("cancel", admin_cancel)],
        per_message=True,  # Добавлено
        per_chat=True,
        per_user=True
    )]