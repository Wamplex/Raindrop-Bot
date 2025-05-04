import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart

TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Бот работает!")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

