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

# Кнопки
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Создать сделку")],
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")],
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить сделку")]],
    resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "👋 Привет! Я — Raindrop Гарант Бот.\n\nВыберите, что вы хотите сделать:",
        reply_markup=main_keyboard
    )

@dp.message(F.text == "✅ Создать сделку")
async def create_deal(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    if user_id in waiting_users:
        await message.answer("❗ У вас уже есть активная сделка.", reply_markup=cancel_keyboard)
        return
    waiting_users[user_id] = {"username": username, "created": datetime.utcnow()}
    await message.answer("📝 Опишите суть сделки и укажите участников.", reply_markup=cancel_keyboard)

    async def reminder():
        await asyncio.sleep(600)
        if user_id in waiting_users:
            await message.answer("⏰ Напоминание: вы не завершили сделку. Нужна помощь?")
    deal_timers[user_id] = asyncio.create_task(reminder())

@dp.message(F.text == "❌ Отменить сделку")
async def cancel_deal(message: Message):
    user_id = message.from_user.id
    if user_id in waiting_users:
        del waiting_users[user_id]
        if user_id in deal_timers:
            deal_timers[user_id].cancel()
            del deal_timers[user_id]
        await message.answer("❌ Сделка отменена.", reply_markup=main_keyboard)
    else:
        await message.answer("ℹ️ У вас нет активной сделки.", reply_markup=main_keyboard)

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("📢 Канал с отзывами: https://t.me/raindrop_reviews", reply_markup=main_keyboard)

@dp.message(F.text == "🛠 Поддержка")
async def support(message: Message):
    await message.answer("📩 Напишите сюда ваш вопрос, и поддержка скоро ответит.", reply_markup=main_keyboard)

@dp.message(F.text == "📋 Активные сделки")
async def active_deals(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not waiting_users:
        await message.answer("🗂 Активных сделок нет.")
        return
    text = "📋 Активные сделки:\n"
    for uid, data in waiting_users.items():
        text += f"👤 @{data['username']} ({uid})\n"
    await message.answer(text)

@dp.message()
async def fallback(message: Message):
    await message.answer("❓ Пожалуйста, выберите действие с помощью кнопок ниже.", reply_markup=main_keyboard)

async def main():
    print("🤖 Бот запущен и работает!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

