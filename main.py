import sqlite3
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("8728313424:AAFK7J2_DK0SUkMBX2BckxRXTIdvJZRr0k4")
CHANNEL_ID = "@prvn_oficial"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("db.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS codes (code TEXT PRIMARY KEY, used INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

codes = ["DROPMEPRVN", "dropmeprvn", "Dropmeprvn", "Drop me Prvn", "DROP ME PRVN"]
for c in codes:
    cur.execute("INSERT OR IGNORE INTO codes VALUES (?,0)", (c,))
conn.commit()

async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Подпишись на канал и отправь код")

@dp.message()
async def handle(msg: types.Message):
    user_id = msg.from_user.id
    code = msg.text.strip()

    if not await check_sub(user_id):
        await msg.answer("❌ Подпишись на канал")
        return

    cur.execute("SELECT used FROM codes WHERE code=?", (code,))
    row = cur.fetchone()

    if not row or row[0] == 1:
        await msg.answer("❌ Код неверный")
        return

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cur.fetchone():
        await msg.answer("❌ Уже получал")
        return

    cur.execute("UPDATE codes SET used=1 WHERE code=?", (code,))
    cur.execute("INSERT INTO users VALUES (?)", (user_id,))
    conn.commit()

    await msg.answer("✅ Код принят! Отправь скриншот, подтверждающий наличие у тебя в кошельке PRVN нашему администратору @PRVN_admin, он отправит тебе 5000 PRVN. Спасибо что ты с нами!")

# Flask
app = Flask('')

@app.route('/')
def home():
    return "alive"

def run_web():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

async def main():
    keep_alive()
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
