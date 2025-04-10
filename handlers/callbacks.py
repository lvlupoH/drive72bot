from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from config import Config
from database import save_callback, save_extra
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging
import traceback

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

# Клавиатура для отмены
CANCEL_KEYBOARD = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога обратного звонка"""
    try:
        query = update.callback_query
        await query.answer()
        context.user_data['request_type'] = 'callback'
        
        await query.message.reply_text(
            "📞 Запрос обратного звонка\n\n"
            "Введите ваше ФИО:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        )
        return NAME
    except Exception as e:
        logger.error(f"Ошибка в start_callback: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def start_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога доп. занятий"""
    try:
        query = update.callback_query
        await query.answer()
        context.user_data['request_type'] = 'extra'
        
        await query.message.reply_text(
            "🎓 Запрос на дополнительные занятия\n\n"
            "Введите ваше ФИО:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        )
        return NAME
    except Exception as e:
        logger.error(f"Ошибка в start_extra: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка имени"""
    try:
        context.user_data['name'] = update.message.text
        await update.message.reply_text(
            "📱 Введите ваш номер телефона:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        )
        return PHONE
    except Exception as e:
        logger.error(f"Ошибка в get_name: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка ввода")
        return ConversationHandler.END

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка телефона"""
    try:
        context.user_data['phone'] = update.message.text
        await update.message.reply_text(
            "❓ Опишите ваш вопрос:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        )
        return QUESTION
    except Exception as e:
        logger.error(f"Ошибка в get_phone: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка ввода")
        return ConversationHandler.END

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация запроса"""
    try:
        user = update.message.from_user
        context.user_data.update({
            'question': update.message.text,
            'username': user.username,
            'user_id': user.id
        })

        # Сохранение в БД
        if context.user_data['request_type'] == 'callback':
            save_callback(context.user_data)
        else:
            save_extra(context.user_data)

        # Отправка email
        await send_request_email(context.user_data)
        
        await update.message.reply_text("✅ Ваш запрос успешно принят!")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Ошибка в get_question: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка обработки запроса")
        return ConversationHandler.END

async def send_request_email(data: dict):
    """Отправка email администратору"""
    try:
        body = f"""
        Новый запрос ({data['request_type'].upper()})
        Пользователь: @{data['username']} (ID: {data['user_id']})
        ФИО: {data['name']}
        Телефон: {data['phone']}
        Вопрос: {data['question']}
        Время: {datetime.now().strftime("%d.%m.%Y %H:%M")}
        """
        
        msg = MIMEText(body.strip())
        msg['Subject'] = f"🚨 Новый запрос: {data['request_type']}"
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.ADMIN_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        logger.error(f"Ошибка отправки email: {str(e)}\n{traceback.format_exc()}")
        raise

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка отмены"""
    await update.message.reply_text("🚫 Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END

def get_callback_handlers():
    """Возвращает обработчики для обратного звонка и доп. занятий"""
    return [
        ConversationHandler(
            entry_points=[CallbackQueryHandler(start_callback, pattern="^callback_request$")],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
                QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(start_extra, pattern="^extra_lessons$")],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
                QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )
    ]
