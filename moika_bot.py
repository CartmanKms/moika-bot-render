import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import os

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Переменные ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

# --- Словарь для связи сообщений ---
user_message_map = {}

# --- Хендлер для сообщений от пользователей ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.full_name
    user_id = update.message.from_user.id

    logging.info(f"Получено сообщение от {user_name} ({user_id}): {user_message}")

    if user_message == '❓ Задать вопрос':
        await update.message.reply_text("Напишите свой вопрос, и мы постараемся ответить как можно скорее 📨")
        return
    elif user_message == '⭐ Оставить отзыв':
        await update.message.reply_text("Пожалуйста, напишите ваш отзыв 🙏")
        return
    elif user_message == '📞 Контакты':
        await update.message.reply_text("📍 Адрес: ул. Комсомольская, 29\n📞 Тел: +7 (963) 822-32-01 или 32-32-01")
        return

    # Остальные сообщения — пересылка в группу
    sent_message = await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"📩 Новое сообщение от {user_name} (ID: {user_id}):\n\n{user_message}"
    )
    user_message_map[sent_message.message_id] = user_id
    await update.message.reply_text("Спасибо! Мы получили ваше сообщение ✅")

# --- Хендлер для ответов из группы ---
async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original_msg_id = update.message.reply_to_message.message_id
        text = update.message.text

        if original_msg_id in user_message_map:
            target_user_id = user_message_map[original_msg_id]
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"👨‍🔧 Ответ от поддержки:\n\n{text}"
            )
            logging.info(f"Ответ из группы отправлен пользователю {target_user_id}")
        else:
            logging.info("Сообщение не связано с известным ID")
    else:
        logging.info("Ответ в группе без reply_to_message")

# --- Запуск бота ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(chat_id=GROUP_CHAT_ID), handle_group_reply))

    logging.info("Бот запущен!")
    app.run_polling()
