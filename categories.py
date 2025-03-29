from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config

# Данные пакетов
PACKAGES = {
    "moto": {
        "МОТО1": {
            "desc": (
                "🔹 Базовый курс для начинающих\n"
                "🔹 10 часов практики\n"
                "🔹 Теория ПДД для категории А\n"
                "🔹 Сертификат об окончании"
            ),
            "price": "12 000 ₽"
        },
        "МОТО2": {
            "desc": (
                "🔹 Продвинутый курс\n"
                "🔹 15 часов практики\n"
                "🔹 Индивидуальный график\n"
                "🔹 Страховка на время обучения"
            ),
            "price": "18 000 ₽"
        },
        # Добавьте остальные пакеты аналогично
    },
    "auto": {
        "АВТО1": {
            "desc": (
                "🔹 Стандартный курс В\n"
                "🔹 20 часов вождения\n"
                "🔹 Занятия на автотренажере\n"
                "🔹 Подготовка к экзамену ГИБДД"
            ),
            "price": "25 000 ₽"
        },
        # Добавьте остальные пакеты
    }
}

async def handle_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Категории'"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Категория А, А1", callback_data="cat_moto")],
        [InlineKeyboardButton("Категория В", callback_data="cat_auto")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        text="🏍️🚗 Выберите категорию для обучения:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ пакетов для выбранной категории"""
    query = update.callback_query
    await query.answer()
    category = query.data.split("_")[1]  # cat_moto -> moto
    
    # Формируем клавиатуру
    buttons = []
    for package, data in PACKAGES[category].items():
        btn_text = f"{package} - {data['price']}"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"package_{category}_{package}")])
    
    # Добавляем кнопку назад
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="back_categories")])
    
    await query.edit_message_text(
        text="📦 Выберите пакет обучения:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_package_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Детализация выбранного пакета"""
    query = update.callback_query
    await query.answer()
    
    # Парсим данные из callback_data: package_moto_МОТО1
    _, category, package = query.data.split("_")
    data = PACKAGES[category][package]
    
    # Формируем сообщение
    text = (
        f"📌 Пакет *{package}*\n\n"
        f"*Описание:*\n{data['desc']}\n\n"
        f"*Стоимость:* {data['price']}\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "Для оплаты перейдите по ссылке:\n"
        f"[Оплатить]({Config.PAYMENT_URL})"
    )
    
    # Кнопки
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", url=Config.PAYMENT_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data=f"back_packages_{category}")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    await query.answer()
    
    # Определяем откуда вернуться
    back_type = query.data.split("_")[1]
    
    if back_type == "main":
        await handle_categories(update, context)
    elif back_type == "categories":
        await handle_categories(update, context)
    elif back_type == "packages":
        category = query.data.split("_")[2]
        context.user_data["current_category"] = category
        await show_packages(update, context)

def setup_categories_handlers(application):
    """Регистрация обработчиков категорий"""
    application.add_handler(CallbackQueryHandler(handle_categories, pattern="^categories$"))
    application.add_handler(CallbackQueryHandler(show_packages, pattern="^cat_(moto|auto)$"))
    application.add_handler(CallbackQueryHandler(show_package_details, pattern="^package_.*"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back_(main|categories|packages).*"))