from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_IDS = [7620745738]

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

waiting_users = {}
deal_timers = {}

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать сделку")],
        [KeyboardButton(text="Отзывы")],
        [KeyboardButton(text="Связь с поддержкой")]
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить сделку")]],
    resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я ГАРАНТ-БОТ. Выберите действие:", reply_markup=start_keyboard)

@dp.message(F.text == "Создать сделку")
async def deal_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    if user_id in waiting_users:
        await message.answer("Вы уже начали сделку.", reply_markup=cancel_keyboard)
        return
    waiting_users[user_id] = {
        "username": username,
        "created": datetime.utcnow()
    }
    await message.answer("Пожалуйста, опиши суть сделки и укажи участников.", reply_markup=cancel_keyboard)

    # Напоминание через 10 минут
    async def reminder():
        await asyncio.sleep(600)
        if user_id in waiting_users:
            await message.answer("⏰ Напоминание: вы начали сделку, но не завершили. Нужна помощь?")
    deal_timers[user_id] = asyncio.create_task(reminder())

@dp.message(F.text == "❌ Отменить сделку")
async def cancel_deal(message: Message):
    user_id = message.from_user.id
    if user_id in waiting_users:
        waiting_users.pop(user_id)
        if user_id in deal_timers:
            deal_timers[user_id].cancel()
            deal_timers.pop(user_id)
        await message.answer("❌ Сделка отменена.", reply_markup=start_keyboard)
    else:
        await message.answer("У вас нет активной сделки.", reply_markup=start_keyboard)

@dp.message(F.text == "📋 Активные сделки")
async def list_deals(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not waiting_users:
        await message.answer("Нет активных сделок.")
        return
    text = "📋 Активные сделки:\n"
    for user_id, data in waiting_users.items():
        username = data['username']
        text += f"👤 @{username} ({user_id})\n"
    await message.answer(text)

@dp.message()
async def fallback(message: Message):
    await message.answer("Выберите действие из меню.", reply_markup=start_keyboard)

async def main():
    print("Бот запущен ✅")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
