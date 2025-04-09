from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from config import Config
import logging

logger = logging.getLogger(__name__)
ADMIN_AUTH, ADMIN_2FA, ADMIN_ACTION = range(3)
ADMIN_2FA_CODE = "123456"

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль администратора:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != Config.ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    await update.message.reply_text("🔐 Введите код 2FA:")
    return ADMIN_2FA

async def admin_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_2FA_CODE:
        await update.message.reply_text("❌ Неверный код!")
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton("Список учеников", callback_data="students_list")],
        [InlineKeyboardButton("Добавить ученика", callback_data="add_student")],
        [InlineKeyboardButton("Выход", callback_data="admin_exit")]
    ]
    await update.message.reply_text(
        "⚙️ Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_ACTION

async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Сессия завершена")
    return ConversationHandler.END

def get_admin_handler():
    return [ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)],
            ADMIN_2FA: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_2fa)],
            ADMIN_ACTION: [CallbackQueryHandler(admin_exit, pattern="^admin_exit$")]
        },
        fallbacks=[CommandHandler("cancel", admin_exit)],
        per_message=False  # Исправлено
    )]