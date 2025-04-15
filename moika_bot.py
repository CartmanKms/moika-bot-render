import os
import logging
import asyncio
import threading
import time
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Переменные окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# --- Telegram bot ---
user_message_map = {}

app = ApplicationBuilder().token(BOT_TOKEN).build()

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

    # Остальные сообщения — отправка в группу
    sent_message = await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"📩 Новое сообщение от {user_name} (ID: {user_id}):\n\n{user_message}"
    )
    user_message_map[sent_message.message_id] = user_id
    await update.message.reply_text("Спасибо! Мы получили ваше сообщение ✅")

async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reply_msg = update.message.reply_to_message
        original_msg_id = reply_msg.message_id
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

# --- Регистрируем handlers ---
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(chat_id=GROUP_CHAT_ID), handle_group_reply))

# --- Flask Web App ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Бот запущен! 🚀"

@web_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.run(app.process_update(update))
    return "ok"

@web_app.route('/set-webhook')
def set_webhook():
    if not RENDER_EXTERNAL_URL:
        return "RENDER_EXTERNAL_URL не задан"
    url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}")
    return f"Webhook установлен на {url}\nОтвет Telegram: {response.text}"

# --- Self-ping для Render ---
def self_ping():
    while True:
        try:
            if RENDER_EXTERNAL_URL:
                requests.get(RENDER_EXTERNAL_URL)
                logging.info("🟢 Self-ping выполнен")
            else:
                logging.warning("RENDER_EXTERNAL_URL не задан, self-ping не выполняется")
        except Exception as e:
            logging.warning(f"❌ Ошибка self-ping: {e}")
        time.sleep(300)  # Каждые 5 минут

if __name__ == '__main__':
    threading.Thread(target=self_ping, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)
