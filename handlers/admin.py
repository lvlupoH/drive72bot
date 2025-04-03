from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

ADMIN_PASSWORD = "Drive"
(
    AWAIT_PASSWORD,
    GET_FULLNAME,
    GET_GROUP,
    GET_EXAMS,
    CONFIRM
) = range(5)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return ConversationHandler.END
        
    await update.message.reply_text("Введите пароль админа:")
    return AWAIT_PASSWORD

async def auth_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_PASSWORD:
        await update.message.reply_text("Неверный пароль!")
        return ConversationHandler.END
        
    context.user_data["admin"] = True
    await update.message.reply_text("Введите Telegram ID студента:")
    return GET_FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tg_id"] = update.message.text
    await update.message.reply_text("Введите ФИО студента:")
    return GET_GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text("Введите номер группы:")
    return GET_EXAMS

async def get_exams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group"] = update.message.text
    await update.message.reply_text(
        "Введите даты экзаменов в формате:\n"
        "Внутренний: ДД.ММ.ГГГГ\n"
        "Государственный: ДД.ММ.ГГГГ\n"
        "Практический: ДД.ММ.ГГГГ\n"
        "Адрес: ул. Примерная, 1"
    )
    return CONFIRM

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", update.message.text)
    address = re.search(r"Адрес: (.+)", update.message.text)
    
    with Session() as session:
        student = Student(
            tg_id=context.user_data["tg_id"],
            fullname=context.user_data["fullname"],
            group=context.user_data["group"],
            internal_exam=dates[0],
            state_exam=dates[1],
            practical_exam=dates[2],
            address=address.group(1)
        )
        session.add(student)
        session.commit()
    
    await update.message.reply_text("Студент зарегистрирован!")
    return ConversationHandler.END

def admin_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT, auth_admin)],
            GET_FULLNAME: [MessageHandler(filters.TEXT, get_fullname)],
            GET_GROUP: [MessageHandler(filters.TEXT, get_group)],
            GET_EXAMS: [MessageHandler(filters.TEXT, get_exams)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm_data)]
        },
        fallbacks=[]
    )