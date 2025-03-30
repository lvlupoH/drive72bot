from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CATEGORIES = {
    "cat_a": {
        "title": "🏍 Категория А, А1",
        "packages": {
            "МОТО-Стандарт": {"price": 10000, "desc": "Теория + 10 практических занятий"},
            "МОТО-Продвинутый": {"price": 15000, "desc": "Теория + 15 занятий с инструктором"},
            "МОТО-Интенсив": {"price": 20000, "desc": "Полный курс подготовки к экзамену"},
            "МОТО-VIP": {"price": 25000, "desc": "Персональный инструктор + экзамен"}
        }
    },
    "cat_b": {
        "title": "🚗 Категория В",
        "packages": {
            "АВТО-Базовый": {"price": 20000, "desc": "28 часов вождения + теория"},
            "АВТО-Полный": {"price": 30000, "desc": "56 часов вождения + медкомиссия"},
            "АВТО-Премиум": {"price": 40000, "desc": "Индивидуальный график занятий"},
            "АВТО-Автошкола+": {"price": 50000, "desc": "VIP-обучение с гарантией"}
        }
    }
}

async def handle_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏍 Категория А, А1", callback_data="cat_a")],
        [InlineKeyboardButton("🚗 Категория В", callback_data="cat_b")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(  # Исправлено: добавлена закрывающая скобка
        text="Выберите категорию обучения:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    
    packages = CATEGORIES[category]["packages"]
    buttons = []
    
    sorted_packages = sorted(
        packages.items(),
        key=lambda x: x[1]['price']
    )
    
    for name, data in sorted_packages:
        btn_row = [
            InlineKeyboardButton(
                f"{name} - {data['price']}₽",
                callback_data=f"info_{name}"
            ),
            InlineKeyboardButton(
                "💳 Оплатить",
                url="https://driveavto72.ru/"
            )
        ]
        buttons.append(btn_row)
    
    text = f"{CATEGORIES[category]['title']}\n\n"
    for name, data in sorted_packages:
        text += f"▪️ <b>{name}</b>\nЦена: {data['price']}₽\n{data['desc']}\n\n"
    
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )
