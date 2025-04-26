from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# === НАСТРОЙКИ ===
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === КЛАВИАТУРЫ ===
def get_main_keyboard(user_id):
    keyboard = [
        [KeyboardButton(text="🐠 Товары")],
        [KeyboardButton(text="✅ Сделка"), KeyboardButton(text="👤 Личный кабинет")],
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(text="🛠 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# === ХЕНДЛЕРЫ ===

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать! Выберите действие:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("https://t.me/raindrop_reviews")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: Message):
    await message.answer("🛠 Напишите свой вопрос. Администратор свяжется с вами лично.")

@dp.message(F.text == "👤 Личный кабинет")
async def profile(message: Message):
    await message.answer(
        f"👤 Ваш Telegram ID: {message.from_user.id}\n"
        f"📦 Кол-во оформленных заявок: скоро будет видно"
    )

@dp.message(F.text == "✅ Сделка")
async def start_deal(message: Message):
    await message.answer(
        "📝 Опишите суть сделки и укажите второго участника.\n"
        "Сделка будет активна в течение 10 минут."
    )

@dp.message(F.text == "🛠 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔐 Админ-панель открыта. Здесь будут админ-функции.")

# === ЗАПУСК БОТА ===

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

