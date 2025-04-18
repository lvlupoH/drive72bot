from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_parts = query.data.split('_')
    action = data_parts[1] if len(data_parts) >= 2 else "main"
    
    # Очистка временных данных пользователя
    context.user_data.clear()
    
    if action == "main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Доп. занятия", callback_data="extra_classes")],
            [InlineKeyboardButton("Адреса", callback_data="contacts")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text(
            "🏠 Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif action == "categories":
        keyboard = [
            [InlineKeyboardButton("Категория А, А1", callback_data="cat_a")],
            [InlineKeyboardButton("Категория В", callback_data="cat_b")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "🏍 Выберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
    elif action == "package":
        category = data_parts[2]
        keyboard = [
            [InlineKeyboardButton("Тариф 1", callback_data=f"package_{category}_МОТО1")],
            [InlineKeyboardButton("Тариф 2", callback_data=f"package_{category}_МОТО2")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{category}")]
        ]
        await query.edit_message_text(
            f"📦 Тарифы категории {CATEGORIES[category]['title']}:",
            reply_markup=InlineKeyboardMarkup(keyboard)