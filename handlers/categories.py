from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {"price": 10000, "desc": "Базовый курс"},
            "МОТО2": {"price": 15000, "desc": "Продвинутый курс"},
            "МОТО3": {"price": 18000, "desc": "Профессиональный курс"},
            "МОТО4": {"price": 22000, "desc": "VIP обучение"}
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {"price": 20000, "desc": "Начальный уровень"},
            "АВТО2": {"price": 25000, "desc": "Полный курс"},
            "АВТО3": {"price": 28000, "desc": "Интенсивный курс"},
            "АВТО4": {"price": 32000, "desc": "Персональное обучение"}
        }
    }
}

async def handle_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Категория А, А1", callback_data="cat_a")],
        [InlineKeyboardButton("Категория В", callback_data="cat_b")],
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    
    packages = CATEGORIES[category]["packages"]
    buttons = []
    
    # Добавляем кнопки для каждого тарифа
    for name, data in packages.items():
        buttons.append([
            InlineKeyboardButton(
                f"{name} - {data['price']}₽ | {data['desc']}", 
                callback_data=f"info_{name}"
            ),
            InlineKeyboardButton(
                "💳 Оплатить", 
                url=f"https://driveavto72.ru/contacts?package={name}"
            )
        ])
    
    # Кнопка "Назад"
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\n\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )