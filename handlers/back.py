from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .categories import handle_categories
from .admin import show_admin_menu, list_students
from .personal import handle_personal_cabinet

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Главное меню
    if query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Админ-панель", callback_data="admin")]
        ]
        await query.edit_message_text(
            "🏠 Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
    
    # Возврат к списку категорий
    elif query.data == "back_categories":
        await handle_categories(update, context)
    
    # Возврат в админ-панель
    elif query.data == "back_admin":
        await show_admin_menu(update, context)
    
    # Возврат к списку групп студентов
    elif query.data == "back_groups":
        await list_students(update, context)
    
    # Возврат в личный кабинет
    elif query.data == "back_profile":
        await handle_personal_cabinet(update, context)
    
    # Возврат к предыдущему меню запросов
    elif query.data == "back_requests":
        keyboard = [
            [InlineKeyboardButton("Доп. занятия", callback_data="extra_lessons")],
            [InlineKeyboardButton("Пересдача экзамена", callback_data="retake_exam")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "📋 Меню запросов:",
            reply_markup=InlineKeyboardMarkup(keyboard))

    return None