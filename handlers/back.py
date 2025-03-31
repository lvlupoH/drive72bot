# handlers/back.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .categories import handle_categories
from .instructors import show_instructors

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Главное меню
    if callback_data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Дополнительные занятия", callback_data="extra_lessons")],
            [InlineKeyboardButton("Пересдача", callback_data="retake_exam")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Инструктора", callback_data="instructors")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text(
            text="🏠 Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Назад к категориям
    elif callback_data == "back_categories":
        await handle_categories(update, context)
    
    # Назад к списку инструкторов
    elif callback_data == "instructors":
        await show_instructors(update, context)
    
    # Дополнительные сценарии при необходимости
    else:
        await query.edit_message_text("Возврат в главное меню...")
        await back_main_menu(update, context)

async def back_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=InlineKeyboardMarkup(keyboard)