from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {"price": 10000, "desc": "Базовый курс"},
            "МОТО2": {"price": 15000, "desc": "Продвинутый курс"},
            "МОТО3": {"price": 20000, "desc": "Индивидуальное обучение"},
            "МОТО4": {"price": 25000, "desc": "VIP курс с гарантией"}
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {"price": 20000, "desc": "Начальный уровень"},
            "АВТО2": {"price": 25000, "desc": "Полный курс"},
            "АВТО3": {"price": 30000, "desc": "Интенсивный курс"},
            "АВТО4": {"price": 35000, "desc": "Персональное обучение"}
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
        btn_text = f"{name} - {data['price']}₽\n{data['desc']}"
        btn = InlineKeyboardButton(
            btn_text,
            callback_data=f"package_{name}"
        )
        buttons.append([btn])
    
    # Кнопка оплаты
    buttons.append([
        InlineKeyboardButton("Оплатить", url="https://driveavto72.ru/contacts"),
        InlineKeyboardButton("Назад", callback_data="back_categories")
    ])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\n\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )