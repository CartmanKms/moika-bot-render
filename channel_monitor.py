import logging
import os
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
load_dotenv()


# === НАСТРОЙКИ через переменные окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("GROUP_CHAT_ID")
CONTACT_BUTTON_URL = os.getenv("CONTACT_BUTTON_URL")

logging.basicConfig(level=logging.INFO)

async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    sent_message = None

    if message.photo:
        sent_message = await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=message.photo[-1].file_id,
            caption=message.caption or '',
            parse_mode='HTML'
        )
    elif message.video:
        sent_message = await context.bot.send_video(
            chat_id=CHANNEL_ID,
            video=message.video.file_id,
            caption=message.caption or '',
            parse_mode='HTML'
        )
    elif message.text:
        sent_message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message.text,
            parse_mode='HTML'
        )
    else:
        await message.reply_text("Я могу переслать только текст, фото или видео.")
        return

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📲 Связаться", url=CONTACT_BUTTON_URL)]]
    )
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇",
        reply_to_message_id=sent_message.message_id,
        reply_markup=keyboard
    )

    await message.reply_text("✅ Пост опубликован в канал!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.CaptionRegex('.*') | filters.TEXT, post_handler))
    app.run_polling()
