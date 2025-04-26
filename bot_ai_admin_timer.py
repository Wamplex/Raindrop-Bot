# ------------------------------
# Импорты
# ------------------------------
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

# ------------------------------
# Настройки
# ------------------------------
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwFBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738
DB_FILE = "shop.db"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------------------
# Клавиатуры
# ------------------------------
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🐠 Товары", callback_data="products")],
    [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
    [InlineKeyboardButton(text="🔧 Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
])

products_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎯 Fisch", callback_data="category_fish")],
    [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="category_bloxfruit")]
])

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚒️ Админ-панель", callback_data="admin")],
    [InlineKeyboardButton(text="✅ Сделка", callback_data="deal")]
])

# ------------------------------
# База данных
# ------------------------------
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, mutation TEXT, price INTEGER, quantity INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, product TEXT, action TEXT, time TEXT)''')
conn.commit()

# ------------------------------
# Команды
# ------------------------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Приветствую в магазине!", reply_markup=main_menu)

# ------------------------------
# Хендлеры на кнопки
# ------------------------------
@dp.callback_query()
async def callbacks(call: CallbackQuery):
    if call.data == "products":
        await call.message.edit_text("Выберите категорию:", reply_markup=products_menu)

    elif call.data == "category_fish":
        await call.message.edit_text("🐠 Fisch товары", reply_markup=await fish_menu())

    elif call.data == "category_bloxfruit":
        await call.message.edit_text("🍇 Bloxfruit товары", reply_markup=await bloxfruit_menu())

    elif call.data == "support":
        await call.message.answer("Напишите свой вопрос, администрация скоро ответит вам лично.")

    elif call.data == "profile":
        await call.message.answer(f"Ваш ID: {call.from_user.id}")

    elif call.data == "admin" and call.from_user.id == ADMIN_ID:
        await call.message.answer("🔐 Админ-панель открыта.")

    elif call.data == "deal":
        await call.message.answer("Создать сделку с администратором.")

# ------------------------------
# Функции для товаров
# ------------------------------
async def fish_menu():
    kb = []
    c.execute("SELECT DISTINCT name FROM products WHERE name LIKE '%Fish%'")
    fishes = c.fetchall()
    for fish in fishes:
        kb.append([InlineKeyboardButton(text=fish[0], callback_data=f"buy_{fish[0]}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def bloxfruit_menu():
    kb = []
    c.execute("SELECT DISTINCT name FROM products WHERE name LIKE '%Fruit%'")
    fruits = c.fetchall()
    for fruit in fruits:
        kb.append([InlineKeyboardButton(text=fruit[0], callback_data=f"buy_{fruit[0]}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ------------------------------
# Запуск бота
# ------------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
