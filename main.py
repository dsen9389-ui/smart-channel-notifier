import asyncio
import logging
import os
import aiosqlite
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
logging.basicConfig(level=logging.INFO)
router = Router()

async def init_db():
    async with aiosqlite.connect("bot_data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        await db.commit()

@router.message(CommandStart())
async def handle_start(message: Message):
    async with aiosqlite.connect("bot_data.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (message.from_user.id, message.from_user.username or ""))
        await db.commit()
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Status"), KeyboardButton(text="Help")]],
        resize_keyboard=True
    )
    await message.answer(f"Welcome to Smart Channel Notifier Bot!\nMonitor web pages and push instant alerts to your Telegram channel seamlessly", reply_markup=kb)

@router.message(Command("help"))
@router.message(F.text == "Help")
async def handle_help(message: Message):
    await message.answer("Available commands:\n/start - Initialize bot\n/help - View guidance\n/status - Check operational status")

@router.message(F.text == "Status")
async def handle_status(message: Message):
    await message.answer("System status: All operational parameters nominal.")

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable not set")
    await init_db()
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
