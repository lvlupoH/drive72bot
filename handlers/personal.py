# handlers/personal.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from models import Student, Session

async def check_profile(user_id: int) -> bool:
    """Проверяет наличие профиля пользователя в базе данных"""
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=str(user_id)).first()
        return student is not None

async def handle_personal_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню личного кабинета"""
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    keyboard = [
        [InlineKeyboardButton("📝 Мои данные", callback_data="my_data")],
        [InlineKeyboardButton("📅 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    
    await message.edit_text(
        "Личный кабинет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_profile_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение данных пользователя"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=str(user_id)).first()
        if not student:
            await query.edit_message_text("❌ Профиль не найден!")
            return
        
        text = (
            f"👤 Ваши данные:\n\n"
            f"ФИО: {student.fullname}\n"
            f"Группа: {student.group}\n"
            f"Внутренний экзамен: {student.internal_exam}\n"
            f"Гос. экзамен: {student.state_exam}\n"
            f"Практика: {student.practical_exam}\n"
            f"Адрес: {student.address}"
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать", callback_data="edit_profile")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_profile")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение записей пользователя"""
    query = update.callback_query
    await query.answer()
    
    # Заглушка для демонстрации
    text = "📅 Ваши текущие записи:\n\n1. Доп. занятие - 15.08.2023 10:00\n2. Пересдача экзамена - 20.08.2023"
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="back_profile")]
        ])
    )

def profile_handler():
    """Настройка обработчиков для личного кабинета"""
    return CallbackQueryHandler(
        pattern="^(my_data|my_bookings|back_profile|edit_profile)$",
        callback=handle_profile_actions
    )

async def handle_profile_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Роутер действий личного кабинета"""
    query = update.callback_query
    action = query.data
    
    if action == "my_data":
        await show_profile_data(update, context)
    elif action == "my_bookings":
        await show_bookings(update, context)
    elif action == "back_profile":
        await handle_personal_cabinet(update, context)
    elif action == "edit_profile":
        await update.callback_query.answer("⏳ Редактирование временно недоступно!", show_alert=True)