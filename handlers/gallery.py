from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import logging
import traceback

# Настройка логгера
logger = logging.getLogger(__name__)

async def gallery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Галерея'"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [
                InlineKeyboardButton(
                    "🌐 VK", 
                    url="https://vk.com/drive_72"
                ),
                InlineKeyboardButton(
                    "📢 Telegram-канал", 
                    url="https://t.me/drive_in_soul"
                )
            ],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
        ]
        
        # Редактируем предыдущее сообщение
        await query.edit_message_text(
            text="📸 Наши социальные сети:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка в gallery_handler: {str(e)}\n{traceback.format_exc()}")
        await handle_error(update, context)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик ошибок"""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка при загрузке галереи. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")

def get_gallery_handlers():
    """Возвращает обработчики для раздела галереи"""
    return [
        CallbackQueryHandler(gallery_handler, pattern="^gallery$")
    ]
