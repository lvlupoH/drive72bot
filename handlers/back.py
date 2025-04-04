from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .categories import handle_categories
from .admin import show_admin_menu, list_students, show_group_students

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")]
        ]
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "back_categories":
        await handle_categories(update, context)
        
    elif query.data == "back_admin":
        await show_admin_menu(update, context)
        
    elif query.data == "back_groups":
        await list_students(update, context)
        
    elif query.data.startswith("back_group_"):
        group = query.data.split("_")[2]
        context.user_data["current_group"] = group
        await show_group_students(update, context)
        
    elif query.data == "back_callback":
        await query.edit_message_text(
            "Возврат в главное меню...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")]])
        )

    else:
        await query.edit_message_text("❌ Ошибка навигации")