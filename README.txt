
📄 README.txt — Telegram-бот для автомойки

👤 Автор:
Создан совместно с ChatGPT и твоими золотыми руками 💪

---

🧠 Описание проекта:
Это Telegram-бот для канала автомойки @Moika1. Он умеет:
- Показывать кастомное меню: ❓ Задать вопрос, ⭐ Оставить отзыв, 📞 Контакты.
- Принимать сообщения от пользователей и пересылать в группу.
- Автоматически отвечать клиентам.
- Позволяет админу (тебе) командой /send отправить пост в канал, с кнопкой связи под ним.
- Поддерживает публикацию текста, фото и видео.

---

🔧 Что нужно для запуска:

1. Python 3.10+
2. Установи зависимости:
   pip install python-telegram-bot python-dotenv

3. Создай .env файл в той же папке, что и moika_bot.py. Пример:

BOT_TOKEN=123456789:ABCDEF_YourBotToken
CHANNEL_ID=-100xxxxxxxxxx         # ID канала @Moika1
GROUP_CHAT_ID=-100yyyyyyyyyy      # ID группы для пересылки сообщений
CONTACT_BUTTON_URL=https://t.me/Moika1SupportBot
ADMIN_ID=123456789                # Твой Telegram user ID

---

▶️ Запуск:
    python moika_bot.py

---

✅ Команда для администратора:

- /send текст — опубликовать пост в канал и прикрепить комментарий с кнопкой связи.
  Пример: /send Сегодня скидка на детейлинг!

---

🧪 Полезные команды и фишки:

- Чтобы получить CHANNEL_ID или GROUP_CHAT_ID, можно:
  - Добавить бота в канал/группу.
  - Отправить туда сообщение, включить логирование — бот выведет ID.
- Чтобы бот появлялся внизу канала как кнопка, добавь его как администратора с правом публиковать.

---

📁 Структура проекта:
📁 moika-bot/
├── moika_bot.py
├── .env
└── README.txt

---

Если потерялся — просто открой этот файл и всё вспомнишь 😉
