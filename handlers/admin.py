from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from models import User, Session
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Состояния
(PASSWORD, FIO, GROUP, INTERNAL_EXAM, 
 STATE_EXAM, PRACTICAL_EXAM, ADDRESS, NOTES) = range(8)

# ================== Аутентификация ==================
async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Введите пароль для доступа:")
    return PASSWORD

async def verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Drive":
        await update.message.reply_text("✅ Доступ разрешен!")
        return await show_admin_panel(update, context)
    else:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Добавить ученика", callback_data="add_student")]]
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    return ConversationHandler.END

# ================== Регистрация ученика ==================
async def start_add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Введите ФИО ученика:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("Введите группу ученика:")
    return GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group'] = update.message.text
    await update.message.reply_text("Дата внутреннего экзамена (ГГГГ-ММ-ДД):")
    return INTERNAL_EXAM

async def get_internal_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date = datetime.strptime(update.message.text, "%Y-%m-%d")
        context.user_data['internal_exam'] = date
        await update.message.reply_text("Дата гос. экзамена (ГГГГ-ММ-ДД):")
        return STATE_EXAM
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты!")
        return INTERNAL_EXAM

async def get_state_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date = datetime.strptime(update.message.text, "%Y-%m-%d")
        context.user_data['state_exam'] = date
        await update.message.reply_text("Дата практического экзамена (ГГГГ-ММ-ДД):")
        return PRACTICAL_EXAM
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты!")
        return STATE_EXAM

async def get_practical_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date = datetime.strptime(update.message.text, "%Y-%m-%d")
        context.user_data['practical_exam'] = date
        await update.message.reply_text("Адрес проведения экзаменов:")
        return ADDRESS
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты!")
        return PRACTICAL_EXAM

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Дополнительные заметки:")
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['notes'] = update.message.text
    session = Session()
    try:
        user = User(
            full_name=context.user_data['fio'],
            group=context.user_data['group'],
            internal_exam=context.user_data['internal_exam'],
            state_exam=context.user_data['state_exam'],
            practical_exam=context.user_data['practical_exam'],
            exam_address=context.user_data['address'],
            notes=context.user_data['notes']
        )
        session.add(user)
        session.commit()
        await update.message.reply_text("✅ Ученик успешно зарегистрирован!")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("❌ Ошибка при сохранении!")
    finally:
        session.close()
        context.user_data.clear()
    return ConversationHandler.END

def get_admin_handler():
    return [ConversationHandler(
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
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)],
        allow_reentry=True
    )]