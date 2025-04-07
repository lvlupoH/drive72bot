import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboard, categories_keyboard, back_keyboard, gallery_keyboard
from utils import send_email
from config import Config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния пользователя для запросов обратного звонка и занятий.
class UserState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_question = State()

# Состояния администратора.
class AdminState(StatesGroup):
    waiting_for_password = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Выберите пункт меню:", reply_markup=main_keyboard)

@dp.message_handler(text="Категории")
async def categories(message: types.Message):
    await message.reply("Выберите категорию:", reply_markup=categories_keyboard)

@dp.message_handler(text=["Категория А, А1", "Категория B"])
async def category_details(message: types.Message):
    category_texts = {
        "Категория А, А1": "Пакеты для категории А, А1:\n\n"
                           "Пакет 1: Описание и цена - [Оплата](https://driveavto72.ru/contacts)\n"
                           "Пакет 2: Описание и цена - [Оплата](https://driveavto72.ru/contacts)\n",
        "Категория B": "Пакеты для категории B:\n\n"
                       "Пакет 1: Описание и цена - [Оплата](https://driveavto72.ru/contacts)\n"
                       "Пакет 2: Описание и цена - [Оплата](https://driveavto72.ru/contacts)\n"
    }
    
    await message.reply(category_texts[message.text], reply_markup=back_keyboard, parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(text="Обратный звонок", state=None)
async def callback_request(message: types.Message):
    await UserState.waiting_for_name.set()
    await message.reply("Введите ваше ФИО:", reply_markup=back_keyboard)

@dp.message_handler(state=UserState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await UserState.waiting_for_phone.set()
    await message.reply("Введите ваш контактный номер телефона:")

@dp.message_handler(state=UserState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await UserState.waiting_for_question.set()
    await message.reply("Введите ваш вопрос:")

@dp.message_handler(state=UserState.waiting_for_question)
async def get_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    email_message = f"ФИО: {user_data['name']}\nТелефон: {user_data['phone']}\nВопрос: {message.text}"
    
    if send_email("Запрос на обратный звонок", email_message):
        await message.reply("Ваш запрос отправлен администратору.", reply_markup=main_keyboard)
        await state.finish()
    else:
        await message.reply("Произошла ошибка при отправке запроса.", reply_markup=main_keyboard)

@dp.message_handler(text="Дополнительные занятия", state=None)
async def extra_lessons_request(message: types.Message):
    await UserState.waiting_for_name.set()
    await message.reply("Введите ваше ФИО:", reply_markup=back_keyboard)

@dp.message_handler(text="Инструкторы")
async def instructors(message: types.Message):
    text = "Инструктор 1: Описание и фото\n" \
           "Инструктор 2: Описание и фото\n"  # Добавьте информацию об инструкторах
    await message.reply(text, reply_markup=back_keyboard)

@dp.message_handler(text="Галерея")
async def gallery(message: types.Message):
    await message.reply("Галерея:", reply_markup=gallery_keyboard)

@dp.message_handler(commands=['admin'], state=None)
async def admin_login(message: types.Message):
    await AdminState.waiting_for_password.set()
    await message.reply("Введите пароль администратора:")

@dp.message_handler(state=AdminState.waiting_for_password)
async def admin_panel(message: types.Message, state: FSMContext):
    if message.text == Config.ADMIN_PASSWORD:
        await message.reply("Добро пожаловать в админ-панель!")  # Здесь можно добавить клавиатуру админ-панели.
        await state.finish()
    else:
        await message.reply("Неверный пароль.")
        await state.finish()

@dp.message_handler(text="Назад", state='*')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply("Выберите пункт меню:", reply_markup=main_keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
