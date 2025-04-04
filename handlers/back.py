from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        from .categories import handle_categories
        await handle_categories(update, context)
    elif query.data == "back_categories":
        from .categories import show_packages
        await show_packages(update, context)
    elif query.data == "back_admin":
        from .admin import show_admin_menu
        await show_admin_menu(update, context)
    elif query.data == "back_groups":
        from .admin import list_students
        await list_students(update, context)
    elif query.data == "back_requests":
        keyboard = [
            [InlineKeyboardButton("Доп. занятия", callback_data="extra_lessons")],
            [InlineKeyboardButton("Пересдача экзамена", callback_data="retake_exam")],
            [InlineKeyboardButton("Назад", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "Меню запросов:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )