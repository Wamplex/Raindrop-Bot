import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def get_products_by_category(category):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, mutation, base_price, stock FROM products WHERE category = ?", (category,))
    products = cur.fetchall()
    conn.close()
    return products

def record_order(user_id, product_id):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
    cur.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def get_user_order_count(user_id):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

@dp.message(CommandStart())
async def cmd_start(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🐠 Товары", callback_data="menu_goods")
    builder.button(text="💬 Отзывы", url="https://t.me/raindrop_reviews")
    builder.button(text="🛠 Поддержка", callback_data="support")
    builder.button(text="👤 Личный кабинет", callback_data="profile")
    if msg.from_user.id == ADMIN_ID:
        builder.button(text="🛡 Админ-панель", callback_data="admin")
    await msg.answer("Добро пожаловать!", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "menu_goods")
async def menu_goods(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎣 Fisch", callback_data="cat_Fisch")
    builder.button(text="🍇 Bloxfruit", callback_data="cat_Bloxfruit")
    await callback.message.edit_text("Выберите категорию:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    products = get_products_by_category(category)

    if not products:
        await callback.message.edit_text("Товары не найдены")
        return

    text = f"<b>{category}:</b>\n"
    builder = InlineKeyboardBuilder()
    for pid, name, mutation, price, stock in products:
        title = f"{name} ({mutation})" if mutation else name
        text += f"{hbold(title)} — {price}₽ ({stock} шт.)\n"
        builder.button(text=title, callback_data=f"buy_{pid}")

    builder.button(text="➕ Предложить своё", callback_data=f"offer_{category}")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT name, mutation, base_price, stock FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()

    if not row or row[3] <= 0:
        await callback.message.answer("❌ Товара нет в наличии.")
        return

    record_order(callback.from_user.id, product_id)

    await callback.message.answer("✅ Покупка успешно совершена!")
    await bot.send_message(ADMIN_ID, f"🛒 Новый заказ от <a href='tg://user?id={callback.from_user.id}'>{callback.from_user.full_name}</a> — {row[0]} ({row[1]})")

@dp.callback_query(F.data.startswith("offer_"))
async def offer_product(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    await callback.message.answer("✏️ Напишите название товара и его описание. Мы рассмотрим ваше предложение.")
    dp.data[callback.from_user.id] = category  # временное хранилище

@dp.message()
async def process_offer(msg: Message):
    if msg.from_user.id in dp.data:
        category = dp.data.pop(msg.from_user.id)
        await bot.send_message(ADMIN_ID, f"📥 Предложение от @{msg.from_user.username or msg.from_user.id} в категории {category}:\n{msg.text}",
                               reply_markup=InlineKeyboardBuilder().row(
                                   types.InlineKeyboardButton(text="Принять", callback_data="ok"),
                                   types.InlineKeyboardButton(text="Отклонить", callback_data="no")
                               ).as_markup())
        await msg.answer("✅ Предложение отправлено. Ожидайте ответа администратора.")

@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.answer("🛠 Напишите ваш вопрос. Администратор скоро ответит вам лично.")

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    count = get_user_order_count(callback.from_user.id)
    await callback.message.answer(f"👤 Ваш ID: {callback.from_user.id}\n📦 Заказов: {count}")

@dp.callback_query(F.data == "admin")
async def admin(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("🔐 Админ-панель будет доработана позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
