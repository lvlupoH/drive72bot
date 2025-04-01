# handlers/profile.py (новый файл)
from telegram import Update
from telegram.ext import ContextTypes
from database import get_db

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM users 
                WHERE user_id = ? 
                ORDER BY id DESC 
                LIMIT 1
            ''', (user_id,))
            data = cursor.fetchone()
            
        if not data:
            await update.message.reply_text("❌ Ваша карточка не найдена")
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
        logger.error(f"Profile error: {str(e)}")
        await update.message.reply_text("❌ Ошибка загрузки данных")
