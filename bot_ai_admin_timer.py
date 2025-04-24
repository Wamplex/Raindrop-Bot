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
user_stats = {}

banned_users = set()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Сделка"), KeyboardButton(text="📊 Профиль")],
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
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("🚫 Вы заблокированы в боте.")
        return

    keyboard = main_keyboard
    if user_id in ADMIN_IDS:
        keyboard.keyboard.append([KeyboardButton(text="📋 Активные сделки")])

    await message.answer(
        "😊 Привет! Я — надёжный гарант для сделок.",
        reply_markup=keyboard
    )

@dp.message(F.text == "✅ Сделка")
async def start_deal(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    if user_id in banned_users:
        await message.answer("🚫 Вы заблокированы.")
        return
    if user_id in waiting_users:
        await message.answer("🔄 Вы уже начали сделку.", reply_markup=cancel_keyboard)
        return

    waiting_users[user_id] = {
        "username": username,
        "status": "📝 Ожидает подтверждения",
        "created": datetime.utcnow()
    }
    await message.answer("📝 Опишите суть сделки и укажите второго участника.", reply_markup=cancel_keyboard)

    for admin in ADMIN_IDS:
        await bot.send_message(admin, f"📥 Новая сделка от @{username} ({user_id})")

    async def timeout():
        await asyncio.sleep(600)
        if user_id in waiting_users:
            await message.answer("⏰ Сделка не подтверждена и будет отменена.")
            waiting_users.pop(user_id, None)

    deal_timers[user_id] = asyncio.create_task(timeout())

@dp.message(F.text == "❌ Отменить сделку")
async def cancel_deal(message: Message):
    user_id = message.from_user.id
    if user_id in waiting_users:
        waiting_users.pop(user_id)
        if user_id in deal_timers:
            deal_timers[user_id].cancel()
            del deal_timers[user_id]
        await message.answer("❌ Сделка отменена.", reply_markup=main_keyboard)
    else:
        await message.answer("ℹ️ У вас нет активной сделки.", reply_markup=main_keyboard)

@dp.message(F.text == "📊 Профиль")
async def show_profile(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    stats = user_stats.get(user_id, {"success": 0, "cancelled": 0})

    profile_text = (
        f"👤 Профиль: @{username} ({user_id})
"
        f"📈 Успешных сделок: {stats['success']}
"
        f"❌ Отменённых: {stats['cancelled']}
"
    )
    await message.answer(profile_text, reply_markup=main_keyboard)

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("💬 Канал с отзывами: https://t.me/raindrop_reviews")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: Message):
    await message.answer("📨 Напишите сюда ваш вопрос. Админ скоро ответит.")

@dp.message(F.text == "📋 Активные сделки")
async def list_deals(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not waiting_users:
        await message.answer("🗂 Активных сделок нет.")
        return
    text = "📋 Активные сделки:
"
    for uid, info in waiting_users.items():
        text += f"👤 @{info['username']} ({uid}) — {info['status']}
"
    await message.answer(text)

@dp.message()
async def fallback(message: Message):
    await message.answer("❓ Выберите действие с кнопок ниже.", reply_markup=main_keyboard)

async def main():
    print("🚀 Бот PRO запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
