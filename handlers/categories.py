from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Данные пакетов для категорий
CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {"price": 10000, "desc": "Базовый курс вождения мотоцикла"},
            "МОТО2": {"price": 15000, "desc": "Продвинутый курс с практикой на автодроме"}
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {"price": 20000, "desc": "Курс для начинающих водителей"},
            "АВТО2": {"price": 25000, "desc": "Полный курс с экзаменационной подготовкой"}
        }
    }
}

async def handle_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Категории'"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Категория А, А1", callback_data="cat_a")],
        [InlineKeyboardButton("Категория В", callback_data="cat_b")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🚗 Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ пакетов выбранной категории"""
    query = update.callback_query
    await query.answer()
    category = query.data  # "cat_a" или "cat_b"
    
    # Проверка существования категории
    if category not in CATEGORIES:
        await query.message.reply_text("❌ Ошибка: категория не найдена")
        return
    
    # Формирование кнопок пакетов
    packages = CATEGORIES[category]["packages"]
    buttons = []
    for name, data in packages.items():
        btn = InlineKeyboardButton(
            f"{name} - {data['price']}₽",
            callback_data=f"package_{name}"
        )
        buttons.append([btn])
    
    # Добавление кнопки "Назад"
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"📦 {CATEGORIES[category]['title']}\n\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def back_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Категории", callback_data="categories")],
        [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
        [InlineKeyboardButton("Галерея", callback_data="gallery")],
        [InlineKeyboardButton("Инструктора", callback_data="instructors")],
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
    ]
    
    await query.edit_message_text(
        text="Главное меню:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
