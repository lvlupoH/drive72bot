from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "packages": {
            "МОТО1": {"price": 10000, "desc": "Базовый курс"},
            "МОТО2": {"price": 15000, "desc": "Продвинутый курс"},
            "МОТО3": {"price": 18000, "desc": "Профессиональный курс"},
            "МОТО4": {"price": 22000, "desc": "VIP обучение"}
        }
    },
    "cat_b": {
        "packages": {
            "АВТО1": {"price": 20000, "desc": "Начальный уровень"},
            "АВТО2": {"price": 25000, "desc": "Полный курс"},
            "АВТО3": {"price": 28000, "desc": "Интенсивный курс"},
            "АВТО4": {"price": 32000, "desc": "Персональное обучение"}
        }
    }
}

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    
    buttons = [
        [InlineKeyboardButton(
            f"{name} - {data['price']}₽ | {data['desc']}", 
            callback_data=f"package_{name}"
        )] for name, data in CATEGORIES[category]['packages'].items()
    ]
    
    buttons.append([InlineKeyboardButton("💳 Оплатить", url="https://driveavto72.ru/contacts")])
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=f"{CATEGORIES[category]['title']}\nВыберите пакет:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )