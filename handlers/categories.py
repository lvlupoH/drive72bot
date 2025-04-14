from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "Категория А, А1",
        "packages": {
            "МОТО1": {
                "price": 10000,
                "desc": "Базовый курс",
                "details": "✅ Теория ПДД\n✅ 10 практических занятий\n✅ Учебные материалы"
            },
            "МОТО2": {
                "price": 15000,
                "desc": "Продвинутый курс",
                "details": "✅ Теория ПДД\n✅ 20 практических занятий\n✅ Страховка"
            },
            "МОТО3": {
                "price": 20000,
                "desc": "Базовый курс",
                "details": "✅ Теория ПДД\n✅ 25 практических занятий\n✅ Учебные материалы"
            },
            "МОТО4": {
                "price": 25000,
                "desc": "Продвинутый курс",
                "details": "✅ Теория ПДД\n✅ 30 практических занятий\n✅ Страховка"
            },
        }
    },
    "cat_b": {
        "title": "Категория В",
        "packages": {
            "АВТО1": {
                "price": 20000,
                "desc": "Базовый курс",
                "details": "✅ Теория ПДД\n✅ 10 практических занятий\n✅ Учебные материалы"
            },
            "АВТО2": {
                "price": 25000,
                "desc": "Продвинутый курс",
                "details": "✅ Теория ПДД\n✅ 20 практических занятий\n✅ Страховка"
            },
            "АВТО3": {
                "price": 30000,
                "desc": "Базовый курс",
                "details": "✅ Теория ПДД\n✅ 25 практических занятий\n✅ Учебные материалы"
            },
            "АВТО4": {
                "price": 35000,
                "desc": "Продвинутый курс",
                "details": "✅ Теория ПДД\n✅ 30 практических занятий\n✅ Страховка"
            },
        }
    },
}

async def handle_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Категория А, А1", callback_data="cat_a")],
        [InlineKeyboardButton("Категория В", callback_data="cat_b")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    
    buttons = [
        [InlineKeyboardButton(
            f"{name} - {data['price']}₽", 
            callback_data=f"package_{category}_{name}"
        )] for name, data in CATEGORIES[category]["packages"].items()
    ]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\nВыберите тариф:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_package_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, category, package = query.data.split('_')
    
    details = CATEGORIES[category]["packages"][package]
    
    text = f"""
    🏍 {package}
    💰 Стоимость: {details['price']}₽
    📝 Описание: {details['desc']}
    📌 Включено:
    {details['details']}
    """
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", url="https://driveavto72.ru/contacts")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{category}")]
    ]
    
    await query.edit_message_text(
        text=text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )