# handlers/categories.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

async def handle_categories(update, context):
    """Обработчик кнопки 'Категории'"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏍 Категория А, А1", callback_data="cat_a")],
        [InlineKeyboardButton("🚗 Категория В", callback_data="cat_b")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text="<b>Выберите категорию обучения:</b>\n\n"
             "ℹ️ Подробное описание каждой категории:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def show_moto_packages(update, context):
    """Пакеты для категории А, А1"""
    query = update.callback_query
    await query.answer()
    
    packages = {
        "МОТО1": {
            "desc": "Базовый курс (10 занятий)",
            "price": "15 000₽",
            "details": "Теория ПДД + практика на автодроме"
        },
        "МОТО2": {
            "desc": "Продвинутый курс (15 занятий)", 
            "price": "20 000₽",
            "details": "Городское вождение + ночные занятия"
        },
        "МОТО3": {
            "desc": "Индивидуальные занятия",
            "price": "2 500₽/час",
            "details": "Персональный инструктор"
        },
        "МОТО4": {
            "desc": "Подготовка к экзамену",
            "price": "10 000₽",
            "details": "Марафон перед экзаменом в ГИБДД"
        }
    }
    
    keyboard = []
    for name, data in packages.items():
        btn = InlineKeyboardButton(
            f"{name} - {data['price']}", 
            callback_data=f"moto_{name.lower()}"
        )
        keyboard.append([btn])
    
    keyboard.extend([
        [InlineKeyboardButton("💳 Оплатить онлайн", url=Config.PAYMENT_URL)],
        [InlineKeyboardButton("🔙 Назад", callback_data="categories")]
    ])
    
    text = "<b>Пакеты категории А, А1:</b>\n\n"
    for name, data in packages.items():
        text += f"▪️ <b>{name}</b>\n{data['desc']}\n{data['details']}\n\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def show_auto_packages(update, context):
    """Пакеты для категории В"""
    query = update.callback_query
    await query.answer()
    
    packages = {
        "АВТО1": {
            "desc": "Начальный курс (10 занятий)",
            "price": "25 000₽",
            "details": "Основы вождения на автодроме"
        },
        "АВТО2": {
            "desc": "Полный курс (20 занятий)",
            "price": "45 000₽", 
            "details": "Автодром + городское вождение"
        },
        "АВТО3": {
            "desc": "Интенсивный курс",
            "price": "3 000₽/час",
            "details": "Ускоренная подготовка"
        },
        "АВТО4": {
            "desc": "Повышение квалификации",
            "price": "15 000₽",
            "details": "Для опытных водителей"
        }
    }
    
    keyboard = []
    for name, data in packages.items():
        btn = InlineKeyboardButton(
            f"{name} - {data['price']}", 
            callback_data=f"auto_{name.lower()}"
        )
        keyboard.append([btn])
    
    keyboard.extend([
        [InlineKeyboardButton("💳 Оплатить онлайн", url=Config.PAYMENT_URL)],
        [InlineKeyboardButton("🔙 Назад", callback_data="categories")]
    ])
    
    text = "<b>Пакеты категории В:</b>\n\n"
    for name, data in packages.items():
        text += f"▪️ <b>{name}</b>\n{data['desc']}\n{data['details']}\n\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_back(update, context):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_categories":
        return await handle_categories(update, context)
    elif query.data == "main_menu":
        from . import start  # Импорт здесь для избежания циклических зависимостей
        return await start(update, context)
