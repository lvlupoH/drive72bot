# handlers/profile.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import get_db

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
                data = cur.fetchone()
                
        if not data:
            await update.message.reply_text("❌ Карточка не найдена")
            return

        text = (
            "📂 Личный кабинет:\n\n"
            f"🎓 Категория: {data['category']}\n"
            f"👥 Группа: {data['group_num']}\n"
            f"👤 ФИО: {data['full_name']}\n"
            f"📅 Период обучения: {data['period']}\n"
            f"📝 Внутренний экзамен: {data['internal_exam']}\n"
            f"🏛 Гос. экзамен: {data['state_exam']}\n"
            f"🚗 Практический экзамен: {data['practical_exam']}"
        )
        
        await update.message.reply_text(text)
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка загрузки данных")

def profile_handler():
    return CommandHandler("profile", show_profile)
