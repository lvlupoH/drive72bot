from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from config import Config
from models import User, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Состояния регистрации
PASSWORD, FIO, USER_ID, GROUP, INTERNAL_EXAM, STATE_EXAM, PRACTICAL_EXAM, ADDRESS, NOTES = range(9)

async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога администрирования"""
    await update.message.reply_text("🔐 Введите пароль для доступа к админ-панели:")
    return PASSWORD

async def verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка пароля"""
    if update.message.text.strip() == "Drive":
        await update.message.reply_text("✅ Доступ разрешен!")
        return await admin_panel(update, context)
    else:
        await update.message.reply_text("❌ Неверный пароль! Попробуйте снова или отмените /cancel")
        return ConversationHandler.END

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню админ-панели"""
    keyboard = [[InlineKeyboardButton("📝 Зарегистрировать ученика", callback_data="add_student")]]
    await update.message.reply_text(
        "⚙️ Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало регистрации ученика"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Введите ФИО ученика:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение ФИО"""
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("Введите Telegram ID ученика:")
    return USER_ID

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение ID"""
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ ID должен быть числом! Повторите ввод:")
        return USER_ID
    context.user_data['user_id'] = int(update.message.text)
    await update.message.reply_text("Введите группу ученика:")
    return GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение группы"""
    context.user_data['group'] = update.message.text
    await update.message.reply_text("Дата внутреннего экзамена (ДД.ММ.ГГГГ):")
    return INTERNAL_EXAM

async def parse_date(date_str: str):
    """Парсинг даты"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None

async def get_internal_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение даты внутреннего экзамена"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ:")
        return INTERNAL_EXAM
    context.user_data['internal_exam'] = date
    await update.message.reply_text("Дата гос. экзамена (ДД.ММ.ГГГГ):")
    return STATE_EXAM

async def get_state_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение даты гос. экзамена"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ:")
        return STATE_EXAM
    context.user_data['state_exam'] = date
    await update.message.reply_text("Дата практического экзамена (ДД.ММ.ГГГГ):")
    return PRACTICAL_EXAM

async def get_practical_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение даты практического экзамена"""
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ:")
        return PRACTICAL_EXAM
    context.user_data['practical_exam'] = date
    await update.message.reply_text("Адрес проведения экзаменов:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение адреса"""
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Дополнительные заметки:")
    return NOTES

async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация регистрации"""
    session = Session()
    try:
        user = User(
            user_id=context.user_data['user_id'],
            full_name=context.user_data['fio'],
            group=context.user_data['group'],
            internal_exam=context.user_data['internal_exam'],
            state_exam=context.user_data['state_exam'],
            practical_exam=context.user_data['practical_exam'],
            exam_address=context.user_data['address'],
            notes=update.message.text
        )
        session.add(user)
        session.commit()
        await update.message.reply_text("✅ Ученик успешно зарегистрирован!")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {str(e)}")
        await update.message.reply_text("❌ Ошибка при сохранении данных!")
    finally:
        session.close()
        context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена регистрации"""
    await update.message.reply_text("🚫 Регистрация отменена")
    context.user_data.clear()
    return ConversationHandler.END

def get_admin_handler():
    """Настройка обработчика админ-панели"""
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_login)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT, verify_password)],
                FIO: [MessageHandler(filters.TEXT, get_fio)],
                USER_ID: [MessageHandler(filters.TEXT, get_user_id)],
                GROUP: [MessageHandler(filters.TEXT, get_group)],
                INTERNAL_EXAM: [MessageHandler(filters.TEXT, get_internal_exam)],
                STATE_EXAM: [MessageHandler(filters.TEXT, get_state_exam)],
                PRACTICAL_EXAM: [MessageHandler(filters.TEXT, get_practical_exam)],
                ADDRESS: [MessageHandler(filters.TEXT, get_address)],
                NOTES: [MessageHandler(filters.TEXT, save_data)]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
    ]