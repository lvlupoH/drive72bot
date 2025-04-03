from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from models import Student, Session

async def check_profile(user_id: int):
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=str(user_id)).first()
        return bool(student)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    with Session() as session:
        student = session.query(Student).filter_by(tg_id=str(user_id)).first()
        
    text = (
        f"👤 {student.fullname}\n"
        f"Группа: {student.group}\n"
        f"Внутренний экзамен: {student.internal_exam}\n"
        f"Гос. экзамен: {student.state_exam}\n"
        f"Практика: {student.practical_exam}\n"
        f"Адрес: {student.address}"
    )
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_main")]])
    )

def profile_handler():
    return CallbackQueryHandler(show_profile, pattern="^profile$")