from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .categories import handle_categories
import logging

logger = logging.getLogger(__name__)

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Назад' для всех меню."""
    query = update.callback_query
    
    try:
        # Пытаемся закрыть callback, игнорируем ошибки устаревших запросов
        await query.answer()
    except Exception as e:
        logger.warning(f"Ignored callback error: {str(e)}")
        return

    try:
        if query.data == "back_main":
            # Главное меню
            keyboard = [
                [
                    InlineKeyboardButton("🏍 Категории", callback_data="categories"),
                    InlineKeyboardButton("📞 Обратный звонок", callback_data="callback_request")
                ],
                [
                    InlineKeyboardButton("🎓 Дополнительные занятия", callback_data="extra_lessons"),
                    InlineKeyboardButton("🔄 Пересдача", callback_data="retake_exam")
                ],
                [
                    InlineKeyboardButton("📷 Галерея", callback_data="gallery"),
                    InlineKeyboardButton("👤 Личный кабинет", callback_data="profile")
                ]
            ]
            
            await query.edit_message_text(
                text="🏠 *Главное меню:*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        elif query.data == "back_categories":
            # Возврат к списку категорий
            await handle_categories(update, context)

        elif query.data == "instructors":
            # Обработка возврата к списку инструкторов (если требуется)
            from .instructors import show_instructors
            await show_instructors(update, context)

    except Exception as e:
        logger.error(f"Back handler error: {str(e)}")
        await query.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")
