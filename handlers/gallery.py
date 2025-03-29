# handlers/gallery.py
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ галереи с фотографиями"""
    media = [
        InputMediaPhoto(media=open('gallery/photo1.jpg', 'rb')),
        InputMediaPhoto(media=open('gallery/photo2.jpg', 'rb'))
    ]
    await update.message.reply_media_group(media=media)
