import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("GROUP_CHAT_ID")
CONTACT_BUTTON_URL = os.getenv("CONTACT_BUTTON_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ← Теперь из .env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("❓ Задать вопрос")],
        [KeyboardButton("⭐ Оставить отзыв")],
        [KeyboardButton("📞 Контакты")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите нужный раздел:", reply_markup=reply_markup)

# --- Обработка кнопок ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📞 Контакты":
        await update.message.reply_text("Телефон: +7 (963) 822-32-01 или короткий 32-32-01 если вы в городе\nАдрес: ул. Комсомольская, 29")
    elif text == "⭐ Оставить отзыв":
        await update.message.reply_text("Пожалуйста, оставьте ваш отзыв. Мы ценим ваше мнение!")
    elif text == "❓ Задать вопрос":
        await update.message.reply_text("Напишите ваш вопрос, и мы скоро ответим!")
    else:
        # Здесь можно добавить автоответы позже, если понадобится
        await update.message.reply_text("Спасибо за сообщение! Мы свяжемся с вами в ближайшее время.")

# --- Команда /send (только для администратора) ---
async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите текст поста после команды /send.")
        return

    post_text = ' '.join(context.args)
    bot = context.bot

    try:
        sent_message = await bot.send_message(chat_id=CHANNEL_ID, text=post_text)

        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Связаться с нами", url=CONTACT_BUTTON_URL)]
        ])

        comment_text = "Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇"

        await bot.send_message(chat_id=CHANNEL_ID, text=comment_text, reply_to_message_id=sent_message.message_id, reply_markup=button)

        await update.message.reply_text("Пост успешно опубликован в канал и добавлена кнопка связи.")

    except Exception as e:
        logger.error(f"Ошибка при отправке поста: {e}")
        await update.message.reply_text("Произошла ошибка при публикации поста.")

# --- Запуск бота ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_to_channel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
