# handlers/admin.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from config import Config
from database import get_db
import logging
import re

logger = logging.getLogger(__name__)

# Состояния админ-панели
(
    PASSWORD, CATEGORY, GROUP, 
    FIO, PERIOD, INTERNAL_EXAM, 
    STATE_EXAM, PRACTICAL_EXAM
) = range(8)

DATE_REGEX = r'\d{2}\.\d{2}\.\d{4}'

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен")
        return ConversationHandler.END
        
    await update.message.reply_text("🔒 Введите пароль администратора:")
    return PASSWORD

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Drive":
        await update.message.reply_text("❌ Неверный пароль")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить пользователя", callback_data="add_user")],
        [InlineKeyboardButton("✏️ Редактировать карточку", callback_data="edit_user")]
    ]
    await update.message.reply_text(
        "🛠 Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Введите категорию обучения (A/B):")
    return CATEGORY

async def validate_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text.upper()
    if category not in ('A', 'B'):
        await update.message.reply_text("❌ Некорректная категория. Введите A или B:")
        return CATEGORY
    context.user_data['category'] = category
    await update.message.reply_text("Введите номер группы:")
    return GROUP

async def validate_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    await update.message.reply_text("Введите ФИО студента:")
    return FIO

async def validate_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("Введите период обучения (например: 01.09.2024-01.12.2024):")
    return PERIOD

async def validate_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if '-' not in update.message.text:
        await update.message.reply_text("❌ Неверный формат. Пример: 01.09.2024-01.12.2024")
        return PERIOD
    context.user_data['period'] = update.message.text
    await update.message.reply_text("Введите дату внутреннего экзамена (ДД.ММ.ГГГГ):")
    return INTERNAL_EXAM

async def validate_date(date: str) -> bool:
    return re.fullmatch(DATE_REGEX, date) is not None

async def validate_internal_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        return INTERNAL_EXAM
    context.user_data['internal_exam'] = update.message.text
    await update.message.reply_text("Введите дату гос. экзамена (ДД.ММ.ГГГГ):")
    return STATE_EXAM

async def validate_state_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        return STATE_EXAM
    context.user_data['state_exam'] = update.message.text
    await update.message.reply_text("Введите дату практического экзамена (ДД.ММ.ГГГГ):")
    return PRACTICAL_EXAM

async def save_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_date(update.message.text):
        await update.message.reply_text("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        return PRACTICAL_EXAM
    
    user_data = context.user_data
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO users (
                    user_id, category, group_num, 
                    full_name, period, internal_exam, 
                    state_exam, practical_exam
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                update.message.from_user.id,
                user_data['category'],
                user_data['group'],
                user_data['full_name'],
                user_data['period'],
                user_data['internal_exam'],
                user_data['state_exam'],
                update.message.text
            ))
            conn.commit()
            
        await update.message.reply_text("✅ Карточка студента создана!")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        await update.message.reply_text("❌ Ошибка сохранения данных")
    
    context.user_data.clear()
    return ConversationHandler.END

def get_admin_handler():
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_command)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
                CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_category)],
                GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_group)],
                FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_fio)],
                PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_period)],
                INTERNAL_EXAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_internal_exam)],
                STATE_EXAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_state_exam)],
                PRACTICAL_EXAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_user_data)]
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            conversation_timeout=300
        )
    ]

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Операция отменена")
    context.user_data.clear()
    return ConversationHandler.END
