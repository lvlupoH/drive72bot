from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
import logging
import requests
import traceback

logger = logging.getLogger(__name__)

INSTRUCTORS = [
    {
        "id": 1,
        "name": "Иван Петров",
        "photo": f"{Config.CDN_URL}/instructors/ivan.jpg",
        "description": "Опыт: 10 лет\nКатегории: A, B",
        "car": "Toyota Corolla"
    }
]

async def instructors_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Инструкторы'"""
    try:
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton(instructor["name"], callback_data=f"instructor_{instructor['id']}")]
            for instructor in INSTRUCTORS
        ]
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])
        
        await query.edit_message_text(
            text="🏁 Наши инструкторы:",
            reply_markup=InlineKeyboardMarkup(keyboard)
    
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}\n{traceback.format_exc()}")
        await handle_error(update, context)

async def show_instructor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение информации об инструкторе"""
    try:
        query = update.callback_query
        await query.answer()
        instructor_id = int(query.data.split("_")[1])
        instructor = next(i for i in INSTRUCTORS if i["id"] == instructor_id)
        
        await query.message.reply_photo(
            photo=instructor["photo"],
            caption=f"{instructor['description']}\nАвтомобиль: {instructor['car']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Назад", callback_data="instructors")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}\n{traceback.format_exc()}")
        await handle_error(update, context)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ошибка загрузки информации об инструкторе"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")

def get_instructors_handlers():
    return [
        CallbackQueryHandler(instructors_handler, pattern="^instructors$"),
        CallbackQueryHandler(show_instructor, pattern=r"^instructor_\d+$")
    ]