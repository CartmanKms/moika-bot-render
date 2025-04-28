import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- Загрузка переменных окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))        # ID группы поддержки
CHANNEL_POST_ID = int(os.getenv("CHANNEL_POST_ID"))  # ID канала для публикации кнопки
CONTACT_BUTTON_URL = os.getenv("CONTACT_BUTTON_URL")  # URL для кнопки связи
ADMIN_ID = int(os.getenv("ADMIN_ID"))                  # ID администратора

# --- Настройка логирования ---
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
    await update.message.reply_text(
        "Добро пожаловать! Выберите нужный раздел:",
        reply_markup=reply_markup
    )

# --- Обработка входящих сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Контакты
    if text == "📞 Контакты":
        await update.message.reply_text("📍 Адрес: ул. Комсомольская, 29\n📞 Тел: +7 (963) 822-32-01 или 32-32-01")
        return

    # Начало обратной связи
    if text in ["❓ Задать вопрос", "⭐ Оставить отзыв"]:
        context.user_data['awaiting_feedback'] = text
        await update.message.reply_text("Пожалуйста, напишите сообщение, и мы его получим!")
        return

    # Пришло текстовое сообщение после кнопки
    if context.user_data.get('awaiting_feedback'):
        feedback_type = context.user_data.pop('awaiting_feedback')
        await forward_to_group(update, context, feedback_type)
        # Подтверждение клиенту
        await update.message.reply_text("Спасибо! Ваш запрос принят, мы скоро ответим.")
        return

    # По умолчанию
    await update.message.reply_text("Спасибо за сообщение! Мы свяжемся с вами в ближайшее время.")

# --- Пересылка сообщений в группу поддержки ---
async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE, feedback_type: str):
    user = update.message.from_user
    text = (
        f"Новое сообщение ({feedback_type}):\n"
        f"От: @{user.username or user.first_name}\n"
        f"ID: {user.id}\n"
        f"Сообщение: {update.message.text}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)

# --- Обработка ответов из группы ---
async def group_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        for line in update.message.reply_to_message.text.splitlines():
            if line.startswith("ID: "):
                try:
                    user_id = int(line.replace("ID: ", "").strip())
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=update.message.text
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить сообщение клиенту: {e}")
                break

# --- Команда /send с поддержкой медиа ---
async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    caption = ' '.join(context.args) if context.args else ''
    try:
        sent_message = None
        # Если ответ на сообщение с медиа
        if update.message.reply_to_message:
            original = update.message.reply_to_message
            # Фото
            if original.photo:
                file_id = original.photo[-1].file_id
                sent_message = await context.bot.send_photo(
                    chat_id=CHANNEL_POST_ID,
                    photo=file_id,
                    caption=caption
                )
            # Видео
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
        # Добавляем кнопку под пост
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Связаться", url=CONTACT_BUTTON_URL)]
        ])
        await context.bot.send_message(
            chat_id=CHANNEL_POST_ID,
            text="Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇",
            reply_to_message_id=sent_message.message_id,
            reply_markup=keyboard
        )
        await update.message.reply_text("Пост успешно опубликован.")
    except Exception as e:
        logger.error(f"Ошибка при публикации поста: {e}")
        await update.message.reply_text("Произошла ошибка при публикации поста.")

# --- Запуск бота ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрация хендлеров
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_post))
    app.add_handler(MessageHandler(filters.Chat(chat_id=GROUP_CHAT_ID) & filters.REPLY, group_reply_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен..." )
    app.run_polling()
