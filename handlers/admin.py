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
import hashlib

logger = logging.getLogger(__name__)
ADMIN_AUTH, ADMIN_2FA, ADMIN_ACTION = range(3)

def generate_2fa_code():
    return hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:6]

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return ConversationHandler.END
    context.user_data['2fa_code'] = generate_2fa_code()
    
    # Отправка кода 2FA на почту администратора
    try:
        msg = MIMEText(f"Ваш код: {context.user_data['2fa_code']}")
        msg['Subject'] = 'Код 2FA'
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.ADMIN_EMAIL
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Ошибка отправки 2FA: {e}")
    
    await update.message.reply_text("🔑 Введите пароль администратора:")
    return ADMIN_AUTH

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != Config.ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    await update.message.reply_text("🔐 Введите код из письма:")
    return ADMIN_2FA

async def admin_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != context.user_data.get('2fa_code', ''):
        await update.message.reply_text("❌ Неверный код!")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("Управление учениками", callback_data="students_manage")],
        [InlineKeyboardButton("Выход", callback_data="admin_exit")]
    ]
    
    await update.message.reply_text(
        "⚙️ Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ADMIN_ACTION

async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
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
        per_message=False
    )]