import sqlite3
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@prvn_oficial"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# БАЗА
os.makedirs("/data", exist_ok=True)

conn = sqlite3.connect(
    "/data/db.db",
    check_same_thread=False
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    used INTEGER DEFAULT 0
)
""")
conn.commit()

# КОД (один и тот же навсегда)
codes = ["dropmeprvn"]

for c in codes:
  cur.execute(
    "INSERT OR IGNORE INTO codes (code) VALUES (?)",
    (c,)
)
    )

conn.commit()


# ПРОВЕРКА ПОДПИСКИ
async def check_sub(user_id):

    try:
        member = await bot.get_chat_member(
            CHANNEL_ID,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False


# /START
@dp.message(Command("start"))
async def start(msg: types.Message):

    await msg.answer(
        "Подпишись на канал @prvn_oficial и отправь код (Subscribe to the @prvn_oficial channel and send the code)"
    )


# ОБРАБОТКА КОДА
@dp.message()
async def handle(msg: types.Message):

    user_id = msg.from_user.id

    code = (
        msg.text
        .strip()
        .lower()
        .replace(" ", "")
    )

    # Проверка подписки
    if not await check_sub(user_id):

        await msg.answer(
            "❌Подпишись на канал @prvn_oficial  и отправь код (Subscribe to the @prvn_oficial channel and send the code)"
        )

        return

    # Проверка кода
    cur.execute(
        "SELECT code FROM codes WHERE code=?",
        (code,)
    )

    row = cur.fetchone()

    if not row:

        await msg.answer(
            "❌ Код неверный (The code is incorrect)"

        )

        return

    # УСПЕХ
    await msg.answer(
        "✅ Код принят!\n\n"
        "Отправь скриншот, подтверждающий наличие у тебя в кошельке PRVN нашему администратору @PRVN_admin, он отправит тебе 10.000 PRVN. Спасибо, что ты с нами! (Send a screenshot confirming you have PRVN in your wallet to our administrator @PRVN_admin, and they'll send you 10.000 PRVN. Thank you for being with us!)"
    )


# MAIN
async def main():

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    print("🚀 Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
