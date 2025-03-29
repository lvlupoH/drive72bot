from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import os
from config import Config

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загрузки фотографий в галерею"""
    try:
        # Создаем папку для галереи, если ее нет
        os.makedirs(Config.GALLERY_PATH, exist_ok=True)
        
        # Сохраняем фото
        photo_file = await update.message.photo[-1].get_file()
        file_name = f"photo_{update.message.message_id}.jpg"
        await photo_file.download_to_drive(os.path.join(Config.GALLERY_PATH, file_name))
        
        await update.message.reply_text("✅ Фото успешно добавлено в галерею!")
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка при загрузке фото")
        print(f"Error saving photo: {str(e)}")

async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ галереи"""
    try:
        media = []
        for file in sorted(os.listdir(Config.GALLERY_PATH)):
            if file.endswith(".jpg"):
                media.append(InputMediaPhoto(media=open(os.path.join(Config.GALLERY_PATH, file), 'rb')))
        
        if media:
            await update.message.reply_media_group(media=media)
        else:
            await update.message.reply_text("Галерея пока пуста")
            
    except Exception as e:
        await update.message.reply_text("❌ Ошибка загрузки галереи")
        print(f"Gallery error: {str(e)}")
