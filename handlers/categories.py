from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО-Стандарт": {"price": 10000, "desc": "Теория + 10 практических занятий"},
            "МОТО-Продвинутый": {"price": 15000, "desc": "Теория + 20 занятий + страховка"},
            "МОТО-Интенсив": {"price": 20000, "desc": "Ускоренный курс за 2 недели"},
            "МОТО-ВИП": {"price": 30000, "desc": "Персональный инструктор 24/7"}
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО-Базовый": {"price": 20000, "desc": "Теория + автотренажер"},
            "АВТО-Полный": {"price": 35000, "desc": "Теория + 30 часов вождения"},
            "АВТО-Премиум": {"price": 45000, "desc": "Вождение с инструктором премиум-класса"},
            "АВТО-Семейный": {"price": 50000, "desc": "Скидка 20% для второго члена семьи"}
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
        btn_row = [
            InlineKeyboardButton(f"{name} - {data['price']}₽", callback_data=f"info_{name}"),
            InlineKeyboardButton("Оплата 💳", url="https://driveavto72.ru/")
        ]
        buttons.append(btn_row)
    
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\n\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )