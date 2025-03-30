from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {"price": 10000, "desc": "Базовый курс"},
            "МОТО2": {"price": 15000, "desc": "Продвинутый курс"}
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {"price": 20000, "desc": "Начальный уровень"},
            "АВТО2": {"price": 25000, "desc": "Полный курс"}
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
    
    for name, data in packages.items():
        btn = InlineKeyboardButton(
            f"{name} - {data['price']}₽",
            callback_data=f"package_{name}"
        )
        buttons.append([btn])
    
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\n\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )