import asyncio
import logging
from app import handlers
from aiogram import Bot, Dispatcher
from app.handlers import router
from config import TOKEN


logging.getLogger("aiogram").setLevel(logging.ERROR)

bot = Bot(token=TOKEN)
dp = Dispatcher()







async def main():
    print("Бот запускается...")
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())