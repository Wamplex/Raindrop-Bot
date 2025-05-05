import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus"
ADMIN_ID = 5960193742  # Укажи свой Telegram ID

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# --- Главное меню пользователя ---
user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎁 Забрать приз")]
    ],
    resize_keyboard=True
)

# --- Главное меню админа ---
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# --- Старт ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👋 Привет, админ!", reply_markup=admin_keyboard)
    else:
        await message.answer("Привет! Нажми кнопку ниже, чтобы забрать приз 🎁", reply_markup=user_keyboard)

# --- Обработка нажатий пользователем ---
@dp.message(F.text == "🎁 Забрать приз")
async def prize_handler(message: Message):
    await message.answer(
        "🎉 Свяжитесь с администратором, чтобы забрать приз — @RaindropSpam_bot"
    )

# --- Админ-панель ---
@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📈 Пока что статистика не настроена.")
    else:
        await message.answer("❌ Недостаточно прав.")

@dp.message(F.text == "🔙 Назад")
async def back_to_menu(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔙 Назад в главное меню.", reply_markup=admin_keyboard)

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
