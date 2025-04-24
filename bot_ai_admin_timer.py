
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime, timedelta

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_IDS = [7620745738]  # можно добавить больше админов

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

waiting_users = {}
support_chats = {}
banned_users = set()

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать сделку")],
        [KeyboardButton(text="Отзывы")],
        [KeyboardButton(text="Связь с поддержкой")],
        [KeyboardButton(text="⚙ Админка")]
    ],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Активные сделки")],
        [KeyboardButton(text="🛠 Поддержка")],
        [KeyboardButton(text="🚫 Заблокировать юзера")],
        [KeyboardButton(text="📬 Рассылка")],
        [KeyboardButton(text="📈 Статистика")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

deal_timers = {}

async def deal_timeout_checker():
    while True:
        now = datetime.utcnow()
        expired = []
        for user_id, start_time in deal_timers.items():
            if now - start_time > timedelta(minutes=10):
                expired.append(user_id)
        for user_id in expired:
            await bot.send_message(user_id, "⏰ Напоминание: вы начали сделку, но не завершили её. Нужна помощь?")
            del deal_timers[user_id]
        await asyncio.sleep(60)

@dp.message(F.text == "/start")
@dp.message(F.text == "Назад")
async def start_handler(message: Message):
    ai_tip = (
        "💡 <b>Советы по безопасной сделке:</b>\n"
        "- Не переводите деньги напрямую.\n"
        "- Всегда сохраняйте переписку.\n"
        "- Используйте только этого гаранта."
    )
    await message.answer("Привет! Я ГАРАНТ-БОТ. Выберите действие:", reply_markup=start_keyboard)
    await message.answer(ai_tip, parse_mode="HTML")

@dp.message(F.text == "Создать сделку")
async def deal_handler(message: Message):
    if message.from_user.id in banned_users:
        await message.answer("Вы заблокированы и не можете создавать сделки.")
        return
    await message.answer("Пожалуйста, опиши суть сделки и укажи участников.")
    waiting_users[message.from_user.id] = message.date
    deal_timers[message.from_user.id] = datetime.utcnow()

@dp.message(F.text == "Отзывы")
async def reviews_handler(message: Message):
    await message.answer("Наш канал с отзывами: https://t.me/raindrop_reviews", reply_markup=back_keyboard)

@dp.message(F.text == "Связь с поддержкой")
async def support_handler(message: Message):
    await message.answer("Напишите сюда свой вопрос, и поддержка скоро ответит.", reply_markup=back_keyboard)
    support_chats[message.from_user.id] = None

@dp.message(F.text == "⚙ Админка")
async def admin_panel(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Добро пожаловать в админку!", reply_markup=admin_keyboard)
    else:
        await message.answer("У вас нет доступа.")

@dp.message(F.text == "📋 Активные сделки")
async def show_deals(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not waiting_users:
        await message.answer("Нет активных сделок.")
    else:
        users = "\n".join(str(uid) for uid in waiting_users.keys())
        await message.answer(f"Активные сделки:\n{users}")

@dp.message(F.text == "🛠 Поддержка")
async def show_support(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not support_chats:
        await message.answer("Нет активных обращений.")
    else:
        users = "\n".join(str(uid) for uid in support_chats.keys())
        await message.answer(f"Ожидают поддержки:\n{users}")

@dp.message(F.text == "🚫 Заблокировать юзера")
async def block_user_prompt(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Введи ID пользователя, которого нужно заблокировать. Пример:\nban 123456789")

@dp.message(F.text.startswith("ban "))
async def ban_user(message: Message):
    if message.from_user.id in ADMIN_IDS:
        try:
            user_id = int(message.text.split(" ")[1])
            banned_users.add(user_id)
            await message.answer(f"Пользователь {user_id} заблокирован.")
        except:
            await message.answer("Неверный формат. Пример: ban 123456789")

@dp.message(F.text == "📬 Рассылка")
async def broadcast_prompt(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Напиши сообщение, которое отправить всем. Пример:\nsend Всем привет!")

@dp.message(F.text.startswith("send "))
async def broadcast_message(message: Message):
    if message.from_user.id in ADMIN_IDS:
        text = message.text[5:]
        for user_id in list(waiting_users.keys()) + list(support_chats.keys()):
            try:
                await bot.send_message(user_id, f"[Рассылка]:\n{text}")
            except:
                pass
        await message.answer("Рассылка завершена.")

@dp.message(F.text == "📈 Статистика")
async def stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(f"👥 Пользователей в сделках: {len(waiting_users)}\n🔧 В поддержке: {len(support_chats)}\n🚫 В бане: {len(banned_users)}")

@dp.message()
async def all_messages(message: Message):
    if message.from_user.id in waiting_users:
        text = f"Новое сообщение от @{message.from_user.username or 'без username'}:\n{message.text}"
        await bot.send_message(ADMIN_IDS[0], text)
        del waiting_users[message.from_user.id]
        deal_timers.pop(message.from_user.id, None)
        return

    if message.from_user.id not in ADMIN_IDS:
        if message.from_user.id in support_chats:
            text = f"[ПОДДЕРЖКА] @{message.from_user.username or 'без username'} ({message.from_user.id}):\n{message.text}"
            await bot.send_message(ADMIN_IDS[0], text)
    else:
        if ":" in message.text:
            target_id_str, reply_text = message.text.split(":", 1)
            try:
                target_id = int(target_id_str.strip())
                await bot.send_message(target_id, f"[ПОДДЕРЖКА ОТВЕТ]:\n{reply_text.strip()}")
                await message.answer("Ответ отправлен.")
            except:
                await message.answer("Ошибка: не удалось отправить сообщение.")

async def main():
    print("Бот запущен с таймером, AI и админкой!")
    asyncio.create_task(deal_timeout_checker())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
