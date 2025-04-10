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
from database import save_extra
import logging
from datetime import datetime

# Состояния диалога
NAME, PHONE, QUESTION = range(3)
logger = logging.getLogger(__name__)

# Клавиатура для отмены
CANCEL_KEYBOARD = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_extra")]]

async def start_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога дополнительных занятий"""
    try:
        query = update.callback_query
        await query.answer()
        context.user_data.clear()
        context.user_data['request_type'] = 'extra_lesson'
        
        await query.message.reply_text(
            "🎓 Запрос на дополнительные занятия\n\n"
            "Введите ваше полное ФИО:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        return NAME
    except Exception as e:
        logger.error(f"Extra start error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def extra_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода имени"""
    try:
        context.user_data['name'] = update.message.text
        await update.message.reply_text(
            "📱 Введите ваш контактный номер телефона:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD)
        return PHONE
    except Exception as e:
        logger.error(f"Name error: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка ввода")
        return ConversationHandler.END

async def extra_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода телефона"""
    try:
        context.user_data['phone'] = update.message.text
        await update.message.reply_text(
            "❔ Опишите желаемое расписание и тип занятий:",
            reply_markup=InlineKeyboardMarkup(CANCEL_KEYBOARD))
        return QUESTION
    except Exception as e:
        logger.error(f"Phone error: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка ввода")
        return ConversationHandler.END

async def extra_get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация запроса"""
    try:
        user = update.message.from_user
        context.user_data.update({
            'question': update.message.text,
            'username': user.username,
            'user_id': user.id,
            'date': datetime.now()
        })

        # Сохранение в БД
        save_extra({
            'username': context.user_data['username'],
            'name': context.user_data['name'],
            'phone': context.user_data['phone'],
            'question': context.user_data['question'],
            'type': 'extra'
        })

        await update.message.reply_text("✅ Заявка принята! Мы свяжемся с вами для уточнения деталей.")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Question error: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка обработки запроса")
        return ConversationHandler.END

async def cancel_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка отмены"""
    await update.message.reply_text("🚫 Запрос отменён")
    context.user_data.clear()
    return ConversationHandler.END

def get_extra_handler():
    """Возвращает настроенный обработчик"""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_extra, pattern="^extra_lessons$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, extra_get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, extra_get_phone)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, extra_get_question)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_extra),
            CallbackQueryHandler(cancel_extra, pattern="^cancel_extra$")
        ],
        allow_reentry=True
    )