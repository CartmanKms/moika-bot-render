import os
from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, MessageHandler, filters, ContextTypes

from flask import Flask
from threading import Thread

# --- Flask для пинга ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Бот жив!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # ← твой токен
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # ← ID твоей группы

user_message_map = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.full_name
    user_id = update.message.from_user.id

    if user_message == '❓ Задать вопрос':
        await update.message.reply_text("Напишите свой вопрос, и мы постараемся ответить как можно скорее 📨")
        return
    elif user_message == '⭐ Оставить отзыв':
        await update.message.reply_text("Пожалуйста, напишите ваш отзыв 🙏")
        return
    elif user_message == '📞 Контакты':
        await update.message.reply_text("📍 Адрес: ул. Комсомльская, 29\n📞 Тел: +7 (963) 822-32-01 или 32-32-01")
        return

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

if __name__ == '__main__':
    keep_alive()  # ← запускаем анти-усыплялку

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(chat_id=GROUP_CHAT_ID), handle_group_reply))

    print("Бот запущен ✅")
    app.run_polling()