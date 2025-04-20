import asyncio
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
import time

BOT_TOKEN = "7359752379:AAGYzrq6ZMB9a0wCSCvFKgiQ_F5-uXxU-xs"
CHANNEL_USERNAME = "@Moika1"

bot = Bot(token=BOT_TOKEN)

last_post_id = None


async def check_new_posts():
    global last_post_id

    while True:
        try:
            posts = await bot.get_chat_history(chat_id=CHANNEL_USERNAME, limit=1)
            if posts:
                latest_post = posts[0]
                if latest_post.message_id != last_post_id:
                    last_post_id = latest_post.message_id
                    await send_reply_with_button(latest_post.message_id)
        except TelegramError as e:
            print(f"Ошибка при получении постов: {e}")

        await asyncio.sleep(3600)  # 1 час


async def send_reply_with_button(post_id):
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Связаться", url="https://t.me/Moika1SupportBot")]
        ])
        await bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text="Теперь вы можете связаться с нами прямо в Telegram! Нажмите на кнопку ниже 👇",
            reply_to_message_id=post_id,
            reply_markup=keyboard
        )
        print(f"Кнопка добавлена под постом ID {post_id}")
    except TelegramError as e:
        print(f"Ошибка при отправке кнопки: {e}")


if __name__ == "__main__":
    asyncio.run(check_new_posts())
