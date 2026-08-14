import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
# Установили ваш реальный домен Railway
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://case-lounge-bot-production.up.railway.app/") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎰 Открыть Case Lounge",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    
    username = message.from_user.first_name or "друг"
    
    await message.answer(
        f"👋 С возвращением, **{username}**!\n\nЗапускай приложение и продолжай игру 👇",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
