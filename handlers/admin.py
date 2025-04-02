from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from models import User, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Состояния админ-панели
ADMIN_STATES = {
    'PASSWORD': 0,
    'FIO': 1,
    'GROUP': 2,
    'INTERNAL_EXAM': 3,
    'STATE_EXAM': 4,
    'PRACTICAL_EXAM': 5,
    'ADDRESS': 6,
    'NOTES': 7
}

# Начало диалога админа
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Введите пароль для доступа:")
    return ADMIN_STATES['PASSWORD']

# Проверка пароля
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "Drive":
        keyboard = [[InlineKeyboardButton("➕ Добавить ученика", callback_data="add_student")]]
        await update.message.reply_text(
            "✅ Доступ разрешен!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['is_admin'] = True
        return ConversationHandler.END  # Завершаем первый этап
    else:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END

# Обработчик кнопки "Добавить ученика"
async def start_student_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✏️ Введите ФИО ученика:")
    return ADMIN_STATES['FIO']

# Шаги регистрации
async def process_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("🏷 Введите номер группы:")
    return ADMIN_STATES['GROUP']

async def process_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    await update.message.reply_text("📅 Дата внутреннего экзамена (ДД.ММ.ГГГГ):")
    return ADMIN_STATES['INTERNAL_EXAM']

async def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None

async def process_internal_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 25.12.2023")
        return ADMIN_STATES['INTERNAL_EXAM']
    context.user_data['internal_exam'] = date
    await update.message.reply_text("📅 Дата государственного экзамена (ДД.ММ.ГГГГ):")
    return ADMIN_STATES['STATE_EXAM']

async def process_state_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 30.12.2023")
        return ADMIN_STATES['STATE_EXAM']
    context.user_data['state_exam'] = date
    await update.message.reply_text("📅 Дата практического экзамена (ДД.ММ.ГГГГ):")
    return ADMIN_STATES['PRACTICAL_EXAM']

async def process_practical_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = await parse_date(update.message.text)
    if not date:
        await update.message.reply_text("❌ Неверный формат! Пример: 05.01.2024")
        return ADMIN_STATES['PRACTICAL_EXAM']
    context.user_data['practical_exam'] = date
    await update.message.reply_text("📍 Адрес проведения экзаменов:")
    return ADMIN_STATES['ADDRESS']

async def process_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("📝 Дополнительные заметки:")
    return ADMIN_STATES['NOTES']

async def process_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['notes'] = update.message.text
    try:
        with Session() as session:
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
            await update.message.reply_text("✅ Ученик успешно зарегистрирован!")
    except Exception as e:
        logger.error(f"Ошибка БД: {str(e)}")
        await update.message.reply_text("⚠️ Ошибка сохранения! Проверьте логи.")
    finally:
        context.user_data.clear()
    return ConversationHandler.END

# Настройка обработчиков
def get_admin_handlers():
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_start)],
            states={
                ADMIN_STATES['PASSWORD']: [MessageHandler(filters.TEXT, check_password)],
                ADMIN_STATES['FIO']: [MessageHandler(filters.TEXT, process_fio)],
                ADMIN_STATES['GROUP']: [MessageHandler(filters.TEXT, process_group)],
                ADMIN_STATES['INTERNAL_EXAM']: [MessageHandler(filters.TEXT, process_internal_exam)],
                ADMIN_STATES['STATE_EXAM']: [MessageHandler(filters.TEXT, process_state_exam)],
                ADMIN_STATES['PRACTICAL_EXAM']: [MessageHandler(filters.TEXT, process_practical_exam)],
                ADMIN_STATES['ADDRESS']: [MessageHandler(filters.TEXT, process_address)],
                ADMIN_STATES['NOTES']: [MessageHandler(filters.TEXT, process_notes)]
            },
            fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
            map_to_parent={}
        ),
        CallbackQueryHandler(start_student_registration, pattern="^add_student$")
    ]