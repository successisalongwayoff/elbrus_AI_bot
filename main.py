import asyncio
import os
from aiogram import Bot,Dispatcher
from dotenv import load_dotenv

    
from handlers import router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN не найден")
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(router)
    print("Бот успешно запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
