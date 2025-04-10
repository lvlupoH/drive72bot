from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from config import Config
from database import User, get_db
import bcrypt
import logging
from datetime import datetime
import traceback

# Состояния диалога
PASSWORD, ACTION, ADD_USER, DELETE_USER = range(4)
logger = logging.getLogger(__name__)

# Клавиатура админ-панели
ADMIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📋 Список учеников", callback_data="list_students")],
    [InlineKeyboardButton("➕ Добавить ученика", callback_data="add_student")],
    [InlineKeyboardButton("❌ Удалить ученика", callback_data="delete_student")],
    [InlineKeyboardButton("🔙 Назад", callback_data="admin_exit")]
])

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с админ-панелью"""
    try:
        if update.message.from_user.id != Config.ADMIN_ID:
            await update.message.reply_text("🚫 Доступ запрещен!")
            return ConversationHandler.END
            
        await update.message.reply_text("🔐 Введите пароль администратора:")
        return PASSWORD
    except Exception as e:
        logger.error(f"Admin start error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка пароля администратора"""
    try:
        if bcrypt.checkpw(update.message.text.encode(), Config.ADMIN_PASSWORD_HASH):
            await show_admin_panel(update, context)
            return ACTION
        else:
            await update.message.reply_text("❌ Неверный пароль!")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Password check error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение админ-панели"""
    await update.message.reply_text(
        "⚙️ Административная панель:",
        reply_markup=ADMIN_KEYBOARD
    )

async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список учеников"""
    try:
        query = update.callback_query
        await query.answer()
        
        with get_db() as session:
            students = session.query(User).limit(50).all()
            
            if not students:
                await query.message.reply_text("📭 Список учеников пуст")
                return
            
            response = ["📚 Список учеников:\n"]
            for student in students:
                response.append(
                    f"├ {student.full_name}\n"
                    f"├ @{student.username}\n"
                    f"└ ID: {student.id}\n"
                )
                
            await query.message.reply_text("\n".join(response)[:4000])
            
    except Exception as e:
        logger.error(f"List students error: {str(e)}\n{traceback.format_exc()}")
        await handle_admin_error(update, context)

async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления ученика"""
    try:
        query = update.callback_query
        await query.answer()
        context.user_data['student_data'] = {}
        await query.message.reply_text("Введите username ученика (@username):")
        return ADD_USER
    except Exception as e:
        logger.error(f"Add student start error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def process_student_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных ученика"""
    try:
        current_state = context.user_data.get('student_step', 0)
        text = update.message.text
        
        if current_state == 0:  # Username
            if not text.startswith("@"):
                await update.message.reply_text("❌ Неверный формат username!")
                return ADD_USER
                
            context.user_data['student_data']['username'] = text[1:]
            await update.message.reply_text("Введите ФИО ученика:")
            context.user_data['student_step'] = 1
            return ADD_USER
            
        elif current_state == 1:  # Full Name
            context.user_data['student_data']['full_name'] = text
            await update.message.reply_text("Введите номер телефона:")
            context.user_data['student_step'] = 2
            return ADD_USER
            
        elif current_state == 2:  # Phone
            context.user_data['student_data']['phone'] = text
            await update.message.reply_text("Введите категорию (A/B/C):")
            context.user_data['student_step'] = 3
            return ADD_USER
            
        elif current_state == 3:  # Category
            context.user_data['student_data']['category'] = text.upper()
            await update.message.reply_text("Введите дату окончания обучения (ДД.ММ.ГГГГ):")
            context.user_data['student_step'] = 4
            return ADD_USER
            
        elif current_state == 4:  # End Date
            try:
                end_date = datetime.strptime(text, "%d.%m.%Y")
                context.user_data['student_data']['end_date'] = end_date
                await finalize_student_creation(update, context)
                return ConversationHandler.END
            except ValueError:
                await update.message.reply_text("❌ Неверный формат даты!")
                return ADD_USER
                
    except Exception as e:
        logger.error(f"Student data error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def finalize_student_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финализация создания ученика"""
    try:
        student_data = context.user_data['student_data']
        
        with get_db() as session:
            new_student = User(
                username=student_data['username'],
                full_name=student_data['full_name'],
                phone=student_data['phone'],
                category=student_data['category'],
                end_date=student_data['end_date']
            )
            session.add(new_student)
            session.commit()
            
        await update.message.reply_text("✅ Ученик успешно добавлен!")
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Student creation error: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка при создании ученика!")

async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление ученика"""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("Введите ID ученика для удаления:")
        return DELETE_USER
    except Exception as e:
        logger.error(f"Delete student error: {str(e)}\n{traceback.format_exc()}")
        return ConversationHandler.END

async def confirm_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение удаления ученика"""
    try:
        student_id = int(update.message.text)
        
        with get_db() as session:
            student = session.query(User).filter_by(id=student_id).first()
            if student:
                session.delete(student)
                session.commit()
                await update.message.reply_text(f"✅ Ученик #{student_id} удален!")
            else:
                await update.message.reply_text("❌ Ученик не найден!")
                
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Deletion error: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ Ошибка при удалении!")
        return ConversationHandler.END

async def handle_admin_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок админ-панели"""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка в админ-панели"
        )
    except Exception as e:
        logger.error(f"Critical admin error: {str(e)}")

def get_admin_handlers():
    """Возвращает обработчики для админ-панели"""
    return [
        ConversationHandler(
            entry_points=[CommandHandler("admin", admin_start)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT, check_password)],
                ACTION: [CallbackQueryHandler(list_students, pattern="^list_students$"),
                        CallbackQueryHandler(add_student_start, pattern="^add_student$"),
                        CallbackQueryHandler(delete_student, pattern="^delete_student$")],
                ADD_USER: [MessageHandler(filters.TEXT, process_student_data)],
                DELETE_USER: [MessageHandler(filters.TEXT, confirm_deletion)]
            },
            fallbacks=[CallbackQueryHandler(show_admin_panel, pattern="^admin_exit$")],
            allow_reentry=True
        )
    ]
