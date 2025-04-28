import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CONTACT_BUTTON_URL = os.getenv("CONTACT_BUTTON_URL")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

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
    elif text in ["⭐ Оставить отзыв", "❓ Задать вопрос"]:
        context.user_data['awaiting_feedback'] = text
        await update.message.reply_text("Пожалуйста, напишите сообщение, и мы его получим!")
    else:
        if context.user_data.get('awaiting_feedback'):
            feedback_type = context.user_data.pop('awaiting_feedback')
            await forward_to_group(update, context, feedback_type)
        else:
            await update.message.reply_text("Спасибо за сообщение! Мы свяжемся с вами в ближайшее время.")

# --- Пересылка сообщений в группу ---
async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE, feedback_type: str):
    user = update.message.from_user
    text = f"Новое сообщение ({feedback_type}):\nОт: @{user.username or user.first_name}\nID: {user.id}\nСообщение: {update.message.text}"

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)

# --- Ответ из группы клиенту ---
async def group_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        lines = update.message.reply_to_message.text.splitlines()
        for line in lines:
            if line.startswith("ID: "):
                try:
                    user_id = int(line.replace("ID: ", "").strip())
                    await context.bot.send_message(chat_id=user_id, text=update.message.text)
                except Exception as e:
                    logger.error(f"Не удалось отправить сообщение клиенту: {e}")
                break

# --- Команда /send (только текст) ---
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

# --- Команда /sendmedia (фото/видео/текст) ---
async def send_media_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                    chat_id=CHANNEL_ID,
                    photo=file_id,
                    caption=caption
                )

            elif original.video:
                file_id = original.video.file_id
                sent_message = await context.bot.send_video(
                    chat_id=CHANNEL_ID,
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
                chat_id=CHANNEL_ID,
                text=caption
            )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Связаться", url=CONTACT_BUTTON_URL)]
        ])

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇",
            reply_markup=keyboard,
            reply_to_message_id=sent_message.message_id
        )

        await update.message.reply_text("Пост с медиа успешно опубликован.")

    except Exception as e:
        logger.error(f"Ошибка при публикации медиа-поста: {e}")
        await update.message.reply_text("Произошла ошибка при публикации поста.")

# --- Запуск бота ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_to_channel))
    app.add_handler(CommandHandler("sendmedia", send_media_post))
    app.add_handler(MessageHandler(filters.Chat(chat_id=GROUP_CHAT_ID) & filters.REPLY, group_reply_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
