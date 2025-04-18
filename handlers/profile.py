from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import Config
import psycopg2

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    conn = psycopg2.connect(Config.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE username = %s", (user.username,))
    student = cur.fetchone()
    conn.close()
    
    if not student:
        await query.edit_message_text("❌ Ваш профиль не найден!")
        return
    
    text = f"""
    👤 Личный кабинет:
    Username: @{student[1]}
    ФИО: {student[2]}
    Телефон: {student[3]}
    Категория: {student[4]}
    Группа: {student[5]}
    Период обучения: {student[6]}
    
    📅 Даты экзаменов:
    - Внутренний теория: {student[7]}
    - Гос. теория: {student[8]}
    - Практика: {student[9]}
    
    🏫 Адреса автошколы:
    {Config.SCHOOL_ADDRESS}
    """
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_main")]])
    )