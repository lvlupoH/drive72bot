from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update
import logging

logger = logging.getLogger(__name__)

PACKAGES = {
    "МОТО1": {
        "price": "10000₽",
        "desc": "1) Теоретические занятия 8 часов\n2) Практические занятия 8 часов",
        "category": "moto"
    },
    "МОТО2": {
        "price": "15000₽", 
        "desc": "1) Теоретические занятия 12 часов\n2) Практические занятия 12 часов",
        "category": "moto"
    },
    "АВТО1": {
        "price": "20000₽",
        "desc": "1) Теоретические занятия 16 часов\n2) Практические занятия 10 часов",
        "category": "auto"
    },
    "АВТО2": {
        "price": "25000₽",
        "desc": "1) Теоретические занятия 18 часов\n2) Практические занятия 14 часов",
        "category": "auto"
    }
}

async def handle_categories(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    try:
        keyboard = [
            [InlineKeyboardButton("Категория А, А1", callback_data="cat_moto")],
            [InlineKeyboardButton("Категория В", callback_data="cat_auto")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
        ]
        
        if query.message.text != "Выберите категорию:":
            await query.edit_message_text(
                text="Выберите категорию:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.answer()
            
    except Exception as e:
        logger.error(f"Ошибка в handle_categories: {e}")
        await query.answer("Произошла ошибка. Попробуйте снова.")

async def show_moto_packages(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    try:
        keyboard = []
        for package, data in PACKAGES.items():
            if data["category"] == "moto":
                keyboard.append([InlineKeyboardButton(
                    f"{package} - {data['price']}", 
                    callback_data=f"package_{package.lower()}"
                )])
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_categories")])
        
        await query.edit_message_text(
            text="Доступные пакеты для категории А, А1:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в show_moto_packages: {e}")
        await query.answer("Ошибка загрузки пакетов")

async def show_auto_packages(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    try:
        keyboard = []
        for package, data in PACKAGES.items():
            if data["category"] == "auto":
                keyboard.append([InlineKeyboardButton(
                    f"{package} - {data['price']}", 
                    callback_data=f"package_{package.lower()}"
                )])
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_categories")])
        
        await query.edit_message_text(
            text="Доступные пакеты для категории В:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в show_auto_packages: {e}")
        await query.answer("Ошибка загрузки пакетов")

async def show_package_details(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    try:
        package_key = query.data.split("_")[1].upper()
        package_data = PACKAGES.get(package_key)
        
        if not package_data:
            await query.message.reply_text("Пакет не найден")
            return
        
        payment_button = InlineKeyboardButton(
            "💳 Оплатить", 
            url="https://driveavto72.ru/"
        )
        back_button = InlineKeyboardButton(
            "⬅️ Назад", 
            callback_data=f"back_to_{package_data['category']}_packages"
        )
        
        keyboard = InlineKeyboardMarkup([[payment_button], [back_button]])
        
        await query.edit_message_text(
            text=f"*{package_key}*\n\n{package_data['desc']}\n\nСтоимость: {package_data['price']}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка в show_package_details: {e}")
        await query.answer("Ошибка загрузки деталей пакета")

async def handle_back(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    try:
        back_data = query.data.split("_")
        if len(back_data) < 2:
            await query.message.reply_text("Неверный запрос")
            return
            
        if back_data[1] == "main":
            await handle_categories(update, context)
        elif back_data[1] == "categories":
            await handle_categories(update, context)
        elif back_data[1] == "to" and len(back_data) >= 3:
            category = back_data[2]
            if category == "moto":
                await show_moto_packages(update, context)
            elif category == "auto":
                await show_auto_packages(update, context)
            else:
                await query.answer("Неизвестная категория")
        else:
            await query.answer("Неверный запрос")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_back: {e}")
        await query.answer("Произошла ошибка. Попробуйте снова.")
