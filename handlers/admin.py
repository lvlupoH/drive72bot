from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    CommandHandler, 
    ConversationHandler, 
    MessageHandler, 
    filters
)
from config import Config
from models import User, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Состояния диалога
PASSWORD, FIO, GROUP, INTERNAL_EXAM, STATE_EXAM, PRACTICAL_EXAM, ADDRESS, NOTES = range(8)

# --------------------------------------------
# 1. Аутентификация администратора
# --------------------------------------------
async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога администратора"""
    await update.message.reply_text("🔐 Введите пароль для доступа:")
    return PASSWORD

async def verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка пароля"""
    if update.message.text == "Drive":
        await update.message.reply_text("✅ Доступ разрешен!")
        return await show_admin_panel(update, context)
    else:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END

# --------------------------------------------
# 2. Главное меню админ-панели
# --------------------------------------------
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение панели управления"""
    keyboard = [
        [InlineKeyboardButton("➕ Зарегистрировать ученика", callback_data="add_student")]
    ]
    await update.message.reply_text(
        "📂 Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

# --------------------------------------------
# 3. Процесс регистрации ученика
# --------------------------------------------
async def start_student_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализация регистрации"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("👤 Введите ФИО ученика:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение ФИО"""
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("📚 Введите группу:")
    return GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение группы"""
    context.user_data['group'] = update.message.text
    await update.message.reply_text("📅 Дата внутреннего экзамена (ДД.ММ.ГГГГ):")
    return INTERNAL_EXAM

async def parse_date(date_str: str):
    """Валидация даты"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None

async def get_internal_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка даты внутреннего экзамена"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 31.12.2024")
        return INTERNAL_EXAM
    context.user_data['internal_exam'] = date
    await update.message.reply_text("📅 Дата гос. экзамена (ДД.ММ.ГГГГ):")
    return STATE_EXAM

async def get_state_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка даты гос. экзамена"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 31.12.2024")
        return STATE_EXAM
    context.user_data['state_exam'] = date
    await update.message.reply_text("📅 Дата практического экзамена (ДД.ММ.ГГГГ):")
    return PRACTICAL_EXAM

async def get_practical_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка даты практики"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 31.12.2024")
        return PRACTICAL_EXAM
    context.user_data['practical_exam'] = date
    await update.message.reply_text("📍 Адрес проведения экзаменов:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение адреса"""
    context.user_data['address'] = update.message.text
    await update.message.reply_text("📝 Дополнительные заметки:")
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация регистрации"""
    context.user_data['notes'] = update.message.text
    session = Session()
    
    try:
        new_user = User(
            full_name=context.user_data['fio'],
            group=context.user_data['group'],
            internal_exam=context.user_data['internal_exam'],
            state_exam=context.user_data['state_exam'],
            practical_exam=context.user_data['practical_exam'],
            exam_address=context.user_data['address'],
            notes=context.user_data['notes']
        )
        session.add(new_user)
        session.commit()
        
        # Активация кнопки "Личный кабинет" для ученика
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="✅ Ученик зарегистрирован! Кнопка 'Личный кабинет' активирована."
        )
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        await update.message.reply_text("⚠️ Ошибка сохранения! Проверьте данные.")
        
    finally:
        session.close()
        context.user_data.clear()
    
    return ConversationHandler.END

# --------------------------------------------
# 4. Экспорт обработчиков
# --------------------------------------------
def get_admin_handler():
    """Возвращает настроенный ConversationHandler"""
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_login)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT, verify_password)],
            FIO: [MessageHandler(filters.TEXT, get_fio)],
            GROUP: [MessageHandler(filters.TEXT, get_group)],
            INTERNAL_EXAM: [MessageHandler(filters.TEXT, get_internal_exam)],
            STATE_EXAM: [MessageHandler(filters.TEXT, get_state_exam)],
            PRACTICAL_EXAM: [MessageHandler(filters.TEXT, get_practical_exam)],
            ADDRESS: [MessageHandler(filters.TEXT, get_address)],
            NOTES: [MessageHandler(filters.TEXT, get_notes)]
        },
        fallbacks=[
            CommandHandler("cancel", lambda u, c: ConversationHandler.END),
            MessageHandler(filters.Regex(r"^Отмена$"), lambda u, c: ConversationHandler.END)
        ],
        allow_reentry=True
    )