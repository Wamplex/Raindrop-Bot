# telegram_shop_bot.py
# Telegram-бот с SQLite, товарами, фильтрами, заявками, админкой

import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

conn = sqlite3.connect("shop.db")
c = conn.cursor()

# Таблицы
c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price INTEGER,
    available BOOLEAN,
    quantity INTEGER,
    mutations TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    item TEXT,
    action TEXT,
    quantity INTEGER,
    time TEXT
)
""")
conn.commit()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐠 Товары")],
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")],
        [KeyboardButton(text="👤 Личный кабинет")],
    ], resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu)

@dp.message(F.text == "🐠 Товары")
async def show_categories(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Fisch", callback_data="cat_Fisch")],
        [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="cat_Bloxfruit")],
    ])
    await message.answer("Выберите категорию:", reply_markup=kb)

@dp.callback_query(F.data.startswith("cat_"))
async def list_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    c.execute("SELECT id, name, price FROM products WHERE category=? AND available=1", (category,))
    items = c.fetchall()
    if not items:
        await callback.message.edit_text("Нет доступных товаров.")
        return
    kb = InlineKeyboardMarkup()
    for pid, name, price in items:
        kb.add(InlineKeyboardButton(text=f"{name} — {price}₽", callback_data=f"item_{pid}"))
    await callback.message.edit_text(f"{category}:", reply_markup=kb)

@dp.callback_query(F.data.startswith("item_"))
async def show_product(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    c.execute("SELECT name, price, quantity, mutations FROM products WHERE id=?", (pid,))
    product = c.fetchone()
    if not product:
        await callback.message.edit_text("Товар не найден.")
        return
    name, price, qty, mutations = product
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_{pid}"),
         InlineKeyboardButton(text="🔁 Обмен", callback_data=f"exchange_{pid}")],
    ])
    text = f"{name}\nЦена: {price}₽\nОсталось: {qty}\nМутации: {mutations}"
    await callback.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
@dp.callback_query(F.data.startswith("exchange_"))
async def handle_order(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    action = "buy" if callback.data.startswith("buy") else "exchange"
    c.execute("SELECT name, price FROM products WHERE id=?", (pid,))
    product = c.fetchone()
    if not product:
        await callback.message.answer("Товар не найден.")
        return
    name, price = product
    username = callback.from_user.username or "без username"
    user_id = callback.from_user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO orders (user_id, username, item, action, quantity, time) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, username, name, action, 1, now))
    conn.commit()
    await bot.send_message(ADMIN_ID, f"📩 Запрос от @{username} на {action} товара {name}")
    await callback.message.answer("⌛️ Запрос отправлен. Ожидайте ответа от администрации.")

@dp.message(F.text == "👤 Личный кабинет")
async def show_profile(message: Message):
    user_id = message.from_user.id
    c.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,))
    count = c.fetchone()[0]
    await message.answer(f"👤 Ваш ID: {user_id}\n📦 Заказов оформлено: {count}")

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("Отзывы: https://t.me/raindrop_reviews")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: Message):
    await message.answer("Напишите ваш вопрос. Администратор ответит вам лично.")

@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT id, name, price, available, quantity FROM products")
    items = c.fetchall()
    text = "\n".join([f"{i[0]}. {i[1]} — {i[2]}₽ | {i[4]} шт | {'✅' if i[3] else '❌'}" for i in items])
    await message.answer("🛠 Все товары:\n" + text)

# Запуск
async def main():
    print("🚀 Бот запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
