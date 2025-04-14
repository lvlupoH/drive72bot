from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Разделяем callback_data для определения текущего раздела
    data_parts = query.data.split('_')
    if len(data_parts) < 2:
        return
    
    action = data_parts[1]
    
    # Обработка различных сценариев "Назад"
    if action == "main":
        # Возврат в главное меню
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
        # Возврат к выбору категорий
        keyboard = [
            [InlineKeyboardButton("Категория А", callback_data="cat_a")],
            [InlineKeyboardButton("Категория В", callback_data="cat_b")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "🏍 Выберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "package":
        # Возврат к списку тарифов текущей категории
        category = data_parts[2]  # Например: "cat_a"
        keyboard = [
            [InlineKeyboardButton("Тариф 1", callback_data=f"package_{category}_1")],
            [InlineKeyboardButton("Тариф 2", callback_data=f"package_{category}_2")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"back_categories")]
        ]
        await query.edit_message_text(
            f"📦 Тарифы категории {category.replace('_', ' ').upper()}:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "admin":
        # Возврат в админ-панель
        keyboard = [
            [InlineKeyboardButton("Список учеников", callback_data="students_list")],
            [InlineKeyboardButton("Добавить ученика", callback_data="add_student")],
            [InlineKeyboardButton("🔙 В главное меню", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "⚙ Админ-панель:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Очистка данных пользователя при возврате
    context.user_data.clear()