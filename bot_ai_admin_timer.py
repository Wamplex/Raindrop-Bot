import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime

# Настройки
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738
DB_FILE = "shop.db"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

# База данных
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price INTEGER,
    stock INTEGER,
    mutation TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    product TEXT,
    action TEXT,
    timestamp TEXT
)''')
conn.commit()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="\ud83d\udc20 Товары", callback_data="products")],
    [InlineKeyboardButton(text="\ud83d\udcac Отзывы", url="https://t.me/raindrop_reviews")],
    [InlineKeyboardButton(text="\ud83d\udd27 Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="\ud83d\udc64 Личный кабинет", callback_data="profile")]
])

category_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="\ud83c\udf3f Fisch", callback_data="category_fisch")],
    [InlineKeyboardButton(text="\ud83c\udf47 Bloxfruit", callback_data="category_bloxfruit")]
])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Добро пожаловать!", reply_markup=main_menu)

@dp.callback_query(F.data == "products")
async def show_categories(call: types.CallbackQuery):
    await call.message.answer("Выберите категорию:", reply_markup=category_menu)

@dp.callback_query(F.data == "profile")
async def profile(call: types.CallbackQuery):
    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (call.from_user.id,))
    orders_count = cursor.fetchone()[0]
    await call.message.answer(f"\ud83d\udc64 Ваш ID: {call.from_user.id}\n\ud83d\udd22 Сделок: {orders_count}")

@dp.callback_query(F.data == "support")
async def support(call: types.CallbackQuery):
    await call.message.answer("\ud83d\udd27 Напишите свой вопрос. Администратор ответит вам лично.")

@dp.callback_query(F.data.startswith("category_"))
async def show_products(call: types.CallbackQuery):
    category = call.data.split("_")[1]
    cursor.execute("SELECT DISTINCT name FROM products WHERE category=?", (category,))
    products = cursor.fetchall()
    if not products:
        await call.message.answer("Товары отсутствуют.")
        return
    kb = InlineKeyboardMarkup()
    for product in products:
        kb.add(InlineKeyboardButton(text=product[0], callback_data=f"product_{product[0]}"))
    kb.add(InlineKeyboardButton(text="➕ Предложить своё", callback_data="propose_item"))
    await call.message.answer(f"Товары категории {category}:", reply_markup=kb)

@dp.callback_query(F.data.startswith("product_"))
async def product_details(call: types.CallbackQuery):
    name = call.data.split("_", 1)[1]
    cursor.execute("SELECT mutation, price, stock FROM products WHERE name=?", (name,))
    entries = cursor.fetchall()
    if not entries:
        await call.message.answer("Нет доступных вариантов.")
        return
    text = f"Товар: {name}\n\n"
    kb = InlineKeyboardMarkup()
    for mutation, price, stock in entries:
        if mutation:
            text += f"• {mutation}: {price}₽ ({stock} шт.)\n"
            kb.add(InlineKeyboardButton(text=f"{mutation} ({stock})", callback_data=f"buy_{name}_{mutation}"))
        else:
            text += f"• {price}₽ ({stock} шт.)\n"
            kb.add(InlineKeyboardButton(text=f"Без мутации ({stock})", callback_data=f"buy_{name}_none"))
    await call.message.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def confirm_buy(call: types.CallbackQuery):
    _, name, mutation = call.data.split("_", 2)
    cursor.execute("SELECT price, stock FROM products WHERE name=? AND (mutation=? OR mutation IS NULL)", (name, mutation if mutation != "none" else None))
    product = cursor.fetchone()
    if not product or product[1] <= 0:
        await call.message.answer("Товар отсутствует на складе.")
        return
    cursor.execute("UPDATE products SET stock = stock - 1 WHERE name=? AND (mutation=? OR mutation IS NULL)", (name, mutation if mutation != "none" else None))
    cursor.execute("INSERT INTO orders (user_id, username, product, action, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (call.from_user.id, call.from_user.username, f"{name} {mutation}", "Покупка", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    await call.message.answer("Запрос отправлен. Ожидайте ответа администратора.")
    await bot.send_message(ADMIN_ID, f"\ud83d\udce2 Новый заказ: {name} {mutation} от @{call.from_user.username}")

@dp.callback_query(F.data == "propose_item")
async def propose_item(call: types.CallbackQuery):
    await call.message.answer("Опишите ваш товар и что хотите за него.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
