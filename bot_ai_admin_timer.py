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
all_users = set()
awaiting_broadcast = {}

# Клавиатуры
def get_main_keyboard(user_id):
    keyboard = [
        [KeyboardButton(text="✅ Сделка"), KeyboardButton(text="📊 Профиль")],
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")]
    ]
    if user_id in ADMIN_IDS:
        keyboard.append([KeyboardButton(text="🛠 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Активные сделки"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🚫 Забанить"), KeyboardButton(text="✅ Разбанить")],
        [KeyboardButton(text="📢 Рассылка"), KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить сделку")]],
    resize_keyboard=True
)

# /start
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    all_users.add(user_id)
    if user_id in banned_users:
        await message.answer("🚫 Вы заблокированы в боте.")
        return
    await message.answer("😊 Привет! Я — надёжный гарант для сделок.", reply_markup=get_main_keyboard(user_id))

# Основные команды
@dp.message(F.text == "✅ Сделка")
async def start_deal(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    if user_id in banned_users:
        await message.answer("🚫 Вы заблокированы.")
        return
    if user_id in waiting_users:
        await message.answer("🔄 У вас уже есть активная сделка.", reply_markup=cancel_keyboard)
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
        await message.answer("❌ Сделка отменена.", reply_markup=get_main_keyboard(user_id))
    else:
        await message.answer("ℹ️ У вас нет активной сделки.", reply_markup=get_main_keyboard(user_id))

@dp.message(F.text == "📊 Профиль")
async def show_profile(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    stats = user_stats.get(user_id, {"success": 0, "cancelled": 0})
    await message.answer(
        f"👤 Профиль: @{username} ({user_id})
"
        f"📈 Успешных сделок: {stats['success']}
"
        f"❌ Отменённых: {stats['cancelled']}",
        reply_markup=get_main_keyboard(user_id)
    )

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("💬 Канал с отзывами: https://t.me/raindrop_reviews")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: Message):
    await message.answer("📨 Напишите сюда ваш вопрос. Админ скоро ответит.")

# Админ-панель
@dp.message(F.text == "🛠 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard)

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

@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(
        f"👥 Пользователей: {len(all_users)}
"
        f"🔐 Заблокировано: {len(banned_users)}
"
        f"📋 Активные сделки: {len(waiting_users)}"
    )

@dp.message(F.text == "🚫 Забанить")
async def ban_user_prompt(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("✏️ Введите ID пользователя для бана:")

        awaiting_broadcast[message.from_user.id] = "ban"

@dp.message(F.text == "✅ Разбанить")
async def unban_user_prompt(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("✏️ Введите ID пользователя для разбана:")
        awaiting_broadcast[message.from_user.id] = "unban"

@dp.message(F.text == "📢 Рассылка")
async def broadcast_prompt(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("✏️ Введите сообщение для рассылки:")
        awaiting_broadcast[message.from_user.id] = "broadcast"

@dp.message(F.text == "🔙 Назад")
async def back(message: Message):
    await message.answer("↩️ Возвращаемся в главное меню.", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message()
async def handle_dynamic_admin_input(message: Message):
    user_id = message.from_user.id
    if user_id in awaiting_broadcast:
        action = awaiting_broadcast.pop(user_id)
        if action == "ban":
            try:
                target_id = int(message.text.strip())
                banned_users.add(target_id)
                await message.answer(f"✅ Пользователь {target_id} забанен.")
            except:
                await message.answer("❌ Ошибка: неправильный ID.")
        elif action == "unban":
            try:
                target_id = int(message.text.strip())
                banned_users.discard(target_id)
                await message.answer(f"✅ Пользователь {target_id} разбанен.")
            except:
                await message.answer("❌ Ошибка: неправильный ID.")
        elif action == "broadcast":
            sent = 0
            for uid in all_users:
                try:
                    await bot.send_message(uid, message.text)
                    sent += 1
                except:
                    pass
            await message.answer(f"📬 Сообщение отправлено {sent} пользователям.")

async def main():
    print("🚀 Бот с админ-панелью запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
