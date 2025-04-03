async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
    address_match = re.search(r"Адрес:\s*(.+)", text)
    
    if len(dates) != 3 or not address_match:
        await update.message.reply_text("❌ Неверный формат данных!")
        return ConversationHandler.END
    
    with Session() as session:
        student = Student(
            tg_id=context.user_data["tg_id"],
            fullname=context.user_data["fullname"],
            group=context.user_data["group"],
            internal_exam=dates[0],
            state_exam=dates[1],
            practical_exam=dates[2],
            address=address_match.group(1).strip()
        )
        session.add(student)
        session.commit()
    
    await update.message.reply_text("✅ Студент зарегистрирован!")
    return ConversationHandler.END