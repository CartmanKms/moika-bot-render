import os
import logging
from flask import Flask, request
import telegram
from telegram import Bot, Update

# --- Логирование ---
logging.basicConfig(level=logging.INFO)

# --- Переменные окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# --- Telegram Bot ---
bot = Bot(token=BOT_TOKEN)
user_message_map = {}

# --- Flask Web App ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает ✅"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text
        user_name = update.message.from_user.full_name
        user_id = update.message.from_user.id

        if update.message.chat.type == 'private':
            if text == '❓ Задать вопрос':
                bot.send_message(chat_id, "Напишите свой вопрос, и мы постараемся ответить как можно скорее 📨")
            elif text == '⭐ Оставить отзыв':
                bot.send_message(chat_id, "Пожалуйста, напишите ваш отзыв 🙏")
            elif text == '📞 Контакты':
                bot.send_message(chat_id, "📍 Адрес: ул. Комсомольская, 29\n📞 Тел: +7 (963) 822-32-01 или 32-32-01")
            else:
                sent = bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"📩 Новое сообщение от {user_name} (ID: {user_id}):\n\n{text}"
                )
                user_message_map[sent.message_id] = user_id
                bot.send_message(chat_id, "Спасибо! Мы получили ваше сообщение ✅")

        elif update.message.chat.id == GROUP_CHAT_ID and update.message.reply_to_message:
            reply_msg = update.message.reply_to_message
            original_msg_id = reply_msg.message_id

            if original_msg_id in user_message_map:
                target_user_id = user_message_map[original_msg_id]
                bot.send_message(
                    chat_id=target_user_id,
                    text=f"👨‍🔧 Ответ от поддержки:\n\n{text}"
                )

    return "ok"

@app.route('/set-webhook')
def set_webhook():
    if not RENDER_EXTERNAL_URL:
        return "RENDER_EXTERNAL_URL не задан"
    url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
    response = bot.set_webhook(url=url)
    return f"Webhook установлен на {url} — {response}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
