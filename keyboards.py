from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
main_keyboard.add(
    KeyboardButton("Категории"),
    KeyboardButton("Обратный звонок"),
    KeyboardButton("Дополнительные занятия"),
    KeyboardButton("Инструкторы"),
    KeyboardButton("Галерея")
)

# Меню категорий
categories_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
categories_keyboard.add(
    KeyboardButton("Категория А, А1"),
    KeyboardButton("Категория B"),
    KeyboardButton("Назад")
)

# Клавиатура "Назад"
back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
back_keyboard.add(KeyboardButton("Назад"))

# Галерея (ссылки)
gallery_keyboard = InlineKeyboardMarkup(row_width=1)
gallery_keyboard.add(
    InlineKeyboardButton("VK", url="https://m.vk.com/drive_72?from=search"),
    InlineKeyboardButton("Telegram", url="https://t.me/drive_in_soul")
)
