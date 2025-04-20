import logging
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
BOT_TOKEN = 'твой_токен_бота'
CHANNEL_ID = '@Moika1'  # или ID, например: -1001234567890
CONTACT_BUTTON_URL = 'https://t.me/Moika1SupportBot'

logging.basicConfig(level=logging.INFO)

# === Команда /post ===
async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message:
        return

    sent_message = None

    # Отправка в канал (фото, видео или просто текст)
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

    # Комментарий под постом
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

# === Запуск бота ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.CaptionRegex('.*') | filters.TEXT, post_handler))  # реагирует на /post с любым вложением
    app.run_polling()
