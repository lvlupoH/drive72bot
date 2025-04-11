async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')[1]
    
    if data == "main":
        keyboard = [
            [InlineKeyboardButton("Категории", callback_data="categories")],
            [InlineKeyboardButton("Обратный звонок", callback_data="callback_request")],
            [InlineKeyboardButton("Дополнительные занятия", callback_data="extra_classes")],
            [InlineKeyboardButton("Адреса и контакты", callback_data="contacts")],
            [InlineKeyboardButton("Галерея", callback_data="gallery")],
            [InlineKeyboardButton("Личный кабинет", callback_data="profile")]
        ]
        await query.edit_message_text(
            "🏁 Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )