import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# Настройки
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738
DB_FILE = "shop.db"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

# База данных
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, mutation TEXT, price INTEGER, quantity INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, item_name TEXT, action TEXT, timestamp TEXT)''')
conn.commit()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🐠 Товары", callback_data="products")],
    [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
    [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
])

# Категории товаров
category_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎣 Fisch", callback_data="category_Fisch")],
    [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="category_Bloxfruit")]
])

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer("👋 Добро пожаловать в магазин!", reply_markup=main_menu)

@dp.message(Command('admin'))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔐 Админ-панель запущена!")
    else:
        await message.answer("⛔ У вас нет прав для доступа к админ-панели.")

@dp.callback_query(F.data == "products")
async def show_categories(call: types.CallbackQuery):
    await call.message.answer("Выберите категорию:", reply_markup=category_menu)

@dp.callback_query(F.data.startswith("category_"))
async def show_items(call: types.CallbackQuery):
    category = call.data.split("_")[1]
    cursor.execute("SELECT DISTINCT name FROM products WHERE category=?", (category,))
    products = cursor.fetchall()
    if not products:
        await call.message.answer("Нет товаров в этой категории.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for product in products:
        markup.add(InlineKeyboardButton(text=product[0], callback_data=f"product_{product[0]}"))
    markup.add(InlineKeyboardButton(text="➕ Предложить своё", callback_data="propose_item"))
    await call.message.answer(f"📦 Товары категории {category}:", reply_markup=markup)

@dp.callback_query(F.data.startswith("product_"))
async def show_product_details(call: types.CallbackQuery):
    product_name = call.data.split("_", 1)[1]
    cursor.execute("SELECT mutation, price, quantity FROM products WHERE name=?", (product_name,))
    variants = cursor.fetchall()
    if not variants:
        await call.message.answer("Нет доступных вариантов.")
        return
    text = f"<b>{product_name}</b> доступные варианты:

"
    markup = InlineKeyboardMarkup(row_width=1)
    for mutation, price, quantity in variants:
        text += f"🔹 {mutation}: {price}₽ ({quantity} шт)
"
        markup.add(InlineKeyboardButton(text=f"{mutation} ({quantity} шт)", callback_data=f"buy_{product_name}_{mutation}"))
    await call.message.answer(text, reply_markup=markup)

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery):
    _, product_name, mutation = call.data.split("_", 2)
    cursor.execute("SELECT price, quantity FROM products WHERE name=? AND mutation=?", (product_name, mutation))
    product = cursor.fetchone()
    if not product or product[1] <= 0:
        await call.message.answer("❌ Этот товар закончился.")
        return
    cursor.execute("UPDATE products SET quantity = quantity - 1 WHERE name=? AND mutation=?", (product_name, mutation))
    conn.commit()
    cursor.execute("INSERT INTO orders (user_id, username, item_name, action, timestamp) VALUES (?, ?, ?, ?, datetime('now'))",
                   (call.from_user.id, call.from_user.username, f"{product_name} ({mutation})", "Покупка"))
    conn.commit()
    await call.message.answer("✅ Покупка оформлена. Ожидайте ответа администрации.")
    await bot.send_message(ADMIN_ID, f"🛒 Новый заказ от @{call.from_user.username}: {product_name} ({mutation})")

@dp.callback_query(F.data == "propose_item")
async def propose_item(call: types.CallbackQuery):
    await call.message.answer("✏️ Опишите ваш товар и желаемый обмен. Администратор рассмотрит ваше предложение.")

@dp.callback_query(F.data == "support")
async def support(call: types.CallbackQuery):
    await call.message.answer("🛠 Напишите свой вопрос сюда. Администратор скоро свяжется с вами.")

@dp.callback_query(F.data == "profile")
async def profile(call: types.CallbackQuery):
    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (call.from_user.id,))
    orders_count = cursor.fetchone()[0]
    await call.message.answer(f"👤 Ваш профиль:
ID: {call.from_user.id}
Сделок: {orders_count}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

