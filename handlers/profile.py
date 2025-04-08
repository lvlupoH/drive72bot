from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from models.student import Student
from models.database import get_db

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    student = db.query(Student).filter(Student.username == update.effective_user.username).first()
    
    if not student:
        await update.message.reply_text("❌ Вы еще не зачислены")
        return
    
    text = (
        "📁 Личный кабинет:\n\n"
        f"👤 ФИО: {student.full_name}\n"
        f"📱 Телефон: {student.phone}\n"
        f"👥 Группа: {student.group}\n"
        f"📅 Внутренний экзамен: {student.theory_internal.strftime('%d.%m.%Y')}\n"
        f"🏛️ Гос. экзамен: {student.theory_state.strftime('%d.%m.%Y')}\n"
        f"🚗 Практика: {student.practice.strftime('%d.%m.%Y')}"
    )
    
    await update.message.reply_text(text)

def get_profile_handler():
    return [CallbackQueryHandler(show_profile, pattern="^profile$")]