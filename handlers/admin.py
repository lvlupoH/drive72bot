from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from config import Config
from models import Student, Session
import re
import logging

logger = logging.getLogger(__name__)
ADMIN_PASSWORD = "Drive"

(
    AWAIT_PASSWORD,
    GET_TG_ID,
    GET_FULLNAME,
    GET_GROUP,
    GET_EXAMS,
    CONFIRM
) = range(6)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text("🔑 Введите пароль админа:")
    return AWAIT_PASSWORD

async def auth_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Неверный пароль!")
        return ConversationHandler.END
    await update.message.reply_text("Введите Telegram ID студента (только цифры):")
    return GET_TG_ID

async def get_tg_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ ID должен содержать только цифры!")
        return GET_TG_ID
    context.user_data["tg_id"] = update.message.text
    await update.message.reply_text("Введите ФИО студента:")
    return GET_FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text("Введите номер группы:")
    return GET_GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group"] = update.message.text
    await update.message.reply_text(
        "Введите данные в формате:\n"
        "Внутренний экзамен: ДД.ММ.ГГГГ\n"
        "Гос. экзамен: ДД.ММ.ГГГГ\n"
        "Практика: ДД.ММ.ГГГГ\n"
        "Адрес: ул. Примерная, 1"
    )
    return CONFIRM

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
        address = re.search(r"Адрес:\s*(.+)", text)
        
        if len(dates) != 3 or not address:
            raise ValueError("Некорректный формат данных")
            
        with Session() as session:
            student = Student(
                tg_id=context.user_data["tg_id"],
                fullname=context.user_data["fullname"],
                group=context.user_data["group"],
                internal_exam=dates[0],
                state_exam=dates[1],
                practical_exam=dates[2],
                address=address.group(1).strip()
            )
            session.add(student)
            session.commit()
            
        await update.message.reply_text("✅ Студент зарегистрирован!")
        
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}")
        await update.message.reply_text("❌ Ошибка формата данных! Повторите ввод:")
        return CONFIRM
        
    context.user_data.clear()
    return ConversationHandler.END

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            GET_TG_ID: [MessageHandler(filters.TEXT, get_tg_id)],
            GET_FULLNAME: [MessageHandler(filters.TEXT, get_fullname)],
            GET_GROUP: [MessageHandler(filters.TEXT, get_group)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm_data)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        allow_reentry=True
    )