from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {
                "price": 10000,
                "desc": "Базовый курс",
                "details": "✅ Теория ПДД\n✅ 10 практических занятий\n✅ Поддержка инструктора"
            },
            "МОТО2": {
                "price": 15000,
                "desc": "Продвинутый курс",
                "details": "✅ Теория ПДД\n✅ 20 практических занятий\n✅ Страховка"
            }
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {
                "price": 20000,
                "desc": "Начальный уровень",
                "details": "✅ Теория ПДД\n✅ 15 практических занятий\n✅ Учебные материалы"
            },
            "АВТО2": {
                "price": 25000,
                "desc": "Полный курс",
                "details": "✅ Теория ПДД\n✅ 30 практических занятий\n✅ Экзамен"
            }
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

async def show_package_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    package_name = query.data.split('_')[1]
    
    # Поиск деталей пакета
    for category in CATEGORIES.values():
        if package_name in category["packages"]:
            details = category["packages"][package_name]["details"]
            price = category["packages"][package_name]["price"]
            break
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", url="https://driveavto72.ru/contacts")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"back_{query.data.split('_')[0]}")]
    ]
    
    await query.edit_message_text(
        text=f"📦 {package_name}\n\n{details}\n\nСтоимость: {price}₽",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )