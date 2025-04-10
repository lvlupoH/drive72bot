from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
import logging
import traceback
from .categories import handle_categories
from .instructors import instructors_handler
from . import start

# Настройка логгера
logger = logging.getLogger(__name__)

# Маппинг для навигации
BACK_HANDLERS = {
    "back_main": start.start_menu,
    "back_categories": handle_categories,
    "back_instructors": instructors_handler
}

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок 'Назад'"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Получаем целевое меню из callback_data
        target = query.data.split("_")[1]
        handler = BACK_HANDLERS.get(f"back_{target}", start.start_menu)
        
        # Вызываем соответствующий обработчик
        await handler(update, context)
        
    except Exception as e:
        logger.error(f"Back error: {str(e)}\n{traceback.format_exc()}")
        await handle_back_error(update, context)

async def handle_back_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибок навигации"""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ошибка навигации. Возврат в главное меню...",
        )
        await start.start_menu(update, context)
    except Exception as e:
        logger.error(f"Critical back error: {str(e)}")

def get_back_handler():
    """Возвращает настроенный обработчик"""
    return CallbackQueryHandler(handle_back, pattern=r"^back_")
