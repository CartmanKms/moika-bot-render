import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # для кнопок (обратная связь)
CHANNEL_POST_ID = os.getenv("CHANNEL_POST_ID")  # для публикации постов
CONTACT_BUTTON_URL = os.getenv("CONTACT_BUTTON_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

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
        await update.message.reply_text("Телефон: +7 (999) 123-45-67\nАдрес: г. Москва, ул. Примерная, 1")
    elif text == "⭐ Оставить отзыв":
        await update.message.reply_text("Пожалуйста, оставьте ваш отзыв. Мы ценим ваше мнение!")
    elif text == "❓ Задать вопрос":
        await update.message.reply_text("Напишите ваш вопрос, и мы скоро ответим!")
    else:
        await update.message.reply_text("Спасибо за сообщение! Мы свяжемся с вами в ближайшее время.")

# --- Команда /send с поддержкой медиа ---
async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    caption = " ".join(context.args) if context.args else ""

    try:
        sent_message = None

        if update.message.reply_to_message:
            original = update.message.reply_to_message

            if original.photo:
                file_id = original.photo[-1].file_id
                sent_message = await context.bot.send_photo(
                    chat_id=CHANNEL_POST_ID,
                    photo=file_id,
                    caption=caption
                )

            elif original.video:
                file_id = original.video.file_id
                sent_message = await context.bot.send_video(
                    chat_id=CHANNEL_POST_ID,
                    video=file_id,
                    caption=caption
                )

            else:
                await update.message.reply_text("Ответьте на сообщение с фото или видео.")
                return

        else:
            if not caption:
                await update.message.reply_text("Пожалуйста, укажите текст поста или ответьте на медиа.")
                return

            sent_message = await context.bot.send_message(
                chat_id=CHANNEL_POST_ID,
                text=caption
            )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Связаться", url=CONTACT_BUTTON_URL)]
        ])

        await context.bot.send_message(
            chat_id=CHANNEL_POST_ID,
            text="Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇",
            reply_markup=keyboard,
            reply_to_message_id=sent_message.message_id
        )

        await update.message.reply_text("Пост опубликован.")
    except Exception as e:
        logger.error(f"Ошибка при публикации поста: {e}")
        await update.message.reply_text("Произошла ошибка при публикации поста.")

# --- Запуск бота ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_post))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
