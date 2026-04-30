import sqlite3
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@prvn_oficial"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База данных
conn = sqlite3.connect("db.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    used INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# Один код, но принимается в любом регистре и с пробелами
codes = ["dropmeprvn"]

for c in codes:
    cur.execute("INSERT OR IGNORE INTO codes VALUES (?, 0)", (c,))
conn.commit()


# Проверка подписки
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# /start
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "Подпишись на канал @prvn_oficial и отправь код"
    )


# Обработка сообщений
@dp.message()
async def handle(msg: types.Message):
    user_id = msg.from_user.id
    code = msg.text.strip().lower().replace(" ", "")

    if not await check_sub(user_id):
        await msg.answer("❌ Подпишись на канал @prvn_oficial")
        return

    cur.execute("SELECT used FROM codes WHERE code=?", (code,))
    row = cur.fetchone()

    if not row:
        await msg.answer("❌ Код неверный")
        return

    if row[0] == 1:
        await msg.answer("❌ Этот код уже использован")
        return

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cur.fetchone():
        await msg.answer("❌ Ты уже получал награду")
        return

    cur.execute("UPDATE codes SET used=1 WHERE code=?", (code,))
    cur.execute("INSERT INTO users VALUES (?)", (user_id,))
    conn.commit()

    await msg.answer(
        "✅ Код принят!\n\n"
        "Отправь скриншот, подтверждающий наличие у тебя в кошельке PRVN нашему администратору @PRVN_admin, он отправит тебе 5000 PRVN. Спасибо, что ты с нами!"
    )


# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
