from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
import logging
import requests
import traceback

# Настройка логгера
logger = logging.getLogger(__name__)

# Данные инструкторов (можно перенести в БД)
INSTRUCTORS = [
    {
        "id": 1,
        "name": "Иван Петров",
        "photo_url": f"{Config.CDN_URL}/instructors/ivan.jpg",
        "description": "• Опыт: 10 лет\n• Категории: A, B\n• Автомобиль: Toyota Corolla",
        "achievements": "Победитель региональных соревнований 2022"
    },
    {
        "id": 2,
        "name": "Мария Сидорова",
        "photo_url": f"{Config.CDN_URL}/instructors/maria.jpg",
        "description": "• Опыт: 7 лет\n• Категории: B, C\n• Автомобиль: Kia Rio",
        "achievements": "Лучший инструктор года 2023"
    }
]

async def instructors_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Инструкторы'"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton(instructor["name"], callback_data=f"instructor_{instructor['id']}")]
            for instructor in INSTRUCTORS
        ]
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])
        
        await query.edit_message_text(
            text="🏁 Наши инструкторы:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в instructors_handler: {str(e)}\n{traceback.format_exc()}")
        await handle_error(update, context)

async def show_instructor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение детальной информации об инструкторе"""
    try:
        query = update.callback_query
        await query.answer()
        instructor_id = int(query.data.split("_")[1])
        instructor = next(i for i in INSTRUCTORS if i["id"] == instructor_id)
        
        # Формируем сообщение
        caption = (
            f"🏆 {instructor['name']}\n\n"
            f"{instructor['description']}\n\n"
            f"Достижения:\n{instructor['achievements']}"
        )
        
        # Пытаемся загрузить фото через CDN
        photo_url = await verify_cdn_url(instructor["photo_url"])
        
        # Отправляем фото и информацию
        await query.message.reply_photo(
            photo=photo_url,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ К списку инструкторов", callback_data="instructors")]
            )
        )
    except Exception as e:
        logger.error(f"Ошибка в show_instructor: {str(e)}\n{traceback.format_exc()}")
        await handle_error(update, context)

async def verify_cdn_url(url: str) -> str:
    """Проверка доступности изображения в CDN"""
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return url
        return f"{Config.CDN_URL}/default_instructor.jpg"  # Запасное изображение
    except Exception as e:
        logger.warning(f"CDN недоступен: {str(e)}")
        return "https://via.placeholder.com/400x300?text=Фото+инструктора"

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка при загрузке информации. Пожалуйста, попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_error: {str(e)}")

def get_instructors_handlers():
    """Возвращает обработчики для работы с инструкторами"""
    return [
        CallbackQueryHandler(instructors_handler, pattern="^instructors$"),
        CallbackQueryHandler(show_instructor, pattern=r"^instructor_\d+$")
    ]
