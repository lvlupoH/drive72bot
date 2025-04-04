from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from config import Config
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
NAME, PHONE, QUESTION = range(3)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    await update.callback_query.message.reply_text(
        "📞 Запрос обратного звонка\n\nПожалуйста, введите ваше имя:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    await update.message.reply_text(
        "Теперь введите ваш номер телефона:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    await update.message.reply_text(
        "Кратко опишите ваш вопрос:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    
    try:
        msg = MIMEText(
            f"Имя: {context.user_data['name']}\n"
            f"Телефон: {context.user_data['phone']}\n"
            f"Вопрос: {context.user_data['question']}\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        msg['Subject'] = 'Новый запрос звонка'
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.ADMIN_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
            
        await update.message.reply_text("✅ Ваш запрос успешно отправлен!")
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка!")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Запрос отменен")
    context.user_data.clear()
    return ConversationHandler.END

def setup_callbacks_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
        states={
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ],
            QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_question),
                CallbackQueryHandler(back.back_handler, pattern="^back_")
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True,
        allow_reentry=True
    )